from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from config import Config
from database import db
import os

app = Flask(__name__)
app.config.from_object(Config)

# Use environment variable for secret key in production
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    events = db.get_all_events(active_only=True)[:3]
    return render_template('index.html', events=events)

@app.route('/events')
def events():
    category = request.args.get('category', 'all')
    all_events = db.get_all_events(active_only=True)
    
    if category == 'all':
        filtered_events = all_events
    else:
        filtered_events = [event for event in all_events if event['category'] == category]
    
    categories = list(set(event['category'] for event in all_events))
    return render_template('events.html', events=filtered_events, categories=categories, current_category=category)

@app.route('/projects')
def projects():
    category = request.args.get('category', 'all')
    projects = db.get_all_projects(category)
    categories = db.get_project_categories()
    
    return render_template('projects.html', projects=projects, categories=categories, current_category=category)

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        member_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'major': request.form.get('major'),
            'year': request.form.get('year'),
            'interest': ','.join(request.form.getlist('interest')),
            'experience': request.form.get('experience'),
            'message': request.form.get('message'),
            'newsletter': request.form.get('newsletter') == 'on'
        }
        
        if db.add_club_member(member_data):
            flash(f'Thank you {member_data["name"]}! Your membership application has been received.', 'success')
        else:
            flash('There was an error processing your application. Please try again.', 'error')
        
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/certification')
def certification():
    if session.get('user_logged_in'):
        user_certifications = db.get_user_certifications(session['user_id'])
        return render_template('certification.html', certifications=user_certifications)
    return render_template('certification.html')

@app.route('/generate_certificate', methods=['POST'])
def generate_certificate():
    if not session.get('user_logged_in') and not session.get('admin_logged_in'):
        flash('Please login to generate certificate', 'error')
        return redirect(url_for('user_login'))
    
    cert_data = {
        'user_name': request.form.get('user_name'),
        'certificate_type': request.form.get('certificate_type'),
        'issue_date': request.form.get('issue_date'),
        'skills_verified': request.form.get('skills_verified'),
        'generated_by': session.get('admin_id')
    }
    
    if session.get('user_logged_in'):
        cert_data['user_id'] = session['user_id']
        if not cert_data['user_name']:
            user = db.get_user_by_id(session['user_id'])
            cert_data['user_name'] = user['full_name']
    
    success, result = db.create_certification(cert_data)
    
    if success:
        flash(f'Certificate generated successfully! Your code: {result}', 'success')
        return redirect(url_for('view_certificate', code=result))
    else:
        flash('Failed to generate certificate', 'error')
        return redirect(url_for('certification'))

@app.route('/certificate/<code>')
def view_certificate(code):
    certification = db.get_certification_by_code(code)
    if not certification:
        flash('Certificate not found', 'error')
        return redirect(url_for('certification'))
    
    return render_template('view_certificate.html', cert=certification)

@app.route('/verify_certificate', methods=['POST'])
def verify_certificate():
    code = request.form.get('certificate_code')
    certification = db.get_certification_by_code(code)
    
    if certification:
        return render_template('verify_certificate.html', cert=certification, verified=True)
    else:
        flash('Invalid certificate code', 'error')
        return render_template('verify_certificate.html', verified=False)

@app.route('/register_event/<int:event_id>', methods=['POST'])
def register_event(event_id):
    registration_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'major': request.form.get('major'),
        'year': request.form.get('year')
    }
    
    success, message = db.register_for_event(event_id, registration_data)
    
    if success:
        flash(f'Successfully registered for the event!', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('events'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = db.verify_admin(username, password)
        if admin:
            session['admin_logged_in'] = True
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            session['admin_role'] = admin['role']
            flash(f'Welcome back, {admin["full_name"]}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    session.pop('admin_role', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    events = db.get_all_events(active_only=False)
    registrations = db.get_event_registrations()
    
    return render_template('admin.html', 
                         events=events, 
                         categories=app.config['EVENT_CATEGORIES'],
                         total_registrations=len(registrations))

@app.route('/admin/events/add', methods=['POST'])
@login_required
def add_event():
    event_data = {
        'title': request.form.get('title'),
        'date': request.form.get('date'),
        'time': request.form.get('time'),
        'location': request.form.get('location'),
        'description': request.form.get('description'),
        'category': request.form.get('category'),
        'max_participants': int(request.form.get('max_participants'))
    }
    
    if db.add_event(event_data):
        flash('Event added successfully!', 'success')
    else:
        flash('Error adding event!', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/events/<int:event_id>/toggle', methods=['POST'])
@login_required
def toggle_event(event_id):
    event = db.get_event_by_id(event_id)
    if event:
        new_status = not event['is_active']
        if db.update_event_status(event_id, new_status):
            status = "activated" if new_status else "deactivated"
            flash(f'Event {status} successfully!', 'success')
        else:
            flash('Error updating event!', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    if db.delete_event(event_id):
        flash('Event deleted successfully!', 'success')
    else:
        flash('Error deleting event!', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/registrations')
@login_required
def view_registrations():
    event_id = request.args.get('event_id')
    registrations = db.get_event_registrations(event_id)
    events = db.get_all_events(active_only=False)
    
    current_event = None
    if event_id:
        current_event = db.get_event_by_id(int(event_id))
    
    return render_template('event_registrations.html', 
                         registrations=registrations, 
                         events=events,
                         current_event=current_event)

@app.route('/admin/certifications')
@login_required
def admin_certifications():
    certifications = db.get_all_certifications()
    return render_template('admin_certifications.html', certifications=certifications)

@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        user_data = {
            'username': request.form.get('username'),
            'password': request.form.get('password'),
            'email': request.form.get('email'),
            'full_name': request.form.get('full_name'),
            'major': request.form.get('major'),
            'academic_year': request.form.get('academic_year'),
            'gmu_id': request.form.get('gmu_id')
        }
        
        success, message = db.create_user(user_data)
        if success:
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('user_login'))
        else:
            flash(message, 'error')
    
    return render_template('user_register.html')

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.verify_user(username, password)
        if user:
            session['user_logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('user_login.html')

@app.route('/user/logout')
def user_logout():
    session.pop('user_logged_in', None)
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('user_role', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/user/profile')
def user_profile():
    if not session.get('user_logged_in'):
        return redirect(url_for('user_login'))
    
    user = db.get_user_by_id(session['user_id'])
    return render_template('user_profile.html', user=user)

@app.route('/admin/users')
@login_required
def admin_users():
    users = db.get_all_admins()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
@login_required
def add_admin_user():
    admin_data = {
        'username': request.form.get('username'),
        'password': request.form.get('password'),
        'email': request.form.get('email'),
        'full_name': request.form.get('full_name'),
        'role': request.form.get('role', 'admin')
    }
    
    success, message = db.create_admin_user(admin_data)
    if success:
        flash('Admin user created successfully!', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    db.initialize_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)