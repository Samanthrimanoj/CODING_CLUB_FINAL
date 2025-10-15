import mysql.connector
from mysql.connector import Error
from config import Config
import hashlib
import json

class Database:
    def __init__(self):
        self.config = Config()
    
    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.config.MYSQL_HOST,
                user=self.config.MYSQL_USER,
                password=self.config.MYSQL_PASSWORD,
                database=self.config.MYSQL_DB,
                port=self.config.MYSQL_PORT
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def initialize_database(self):
        connection = self.get_connection()
        if connection is None:
            try:
                connection = mysql.connector.connect(
                    host=self.config.MYSQL_HOST,
                    user=self.config.MYSQL_USER,
                    password=self.config.MYSQL_PASSWORD,
                    port=self.config.MYSQL_PORT
                )
                cursor = connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.MYSQL_DB}")
                cursor.close()
                connection.close()
                connection = self.get_connection()
                if connection is None:
                    return False
            except Error as e:
                print(f"Error creating database: {e}")
                return False
        
        cursor = connection.cursor()
        
        tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                location VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                category VARCHAR(50) NOT NULL,
                max_participants INT NOT NULL,
                current_participants INT DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS event_registrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                major VARCHAR(100),
                academic_year VARCHAR(50),
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                UNIQUE KEY unique_event_email (event_id, email)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS club_members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                major VARCHAR(100),
                academic_year VARCHAR(50),
                interests TEXT,
                experience_level VARCHAR(50),
                message TEXT,
                newsletter_subscription BOOLEAN DEFAULT TRUE,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                technologies JSON,
                category VARCHAR(100) NOT NULL,
                github_url VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS admin_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                role ENUM('super_admin', 'admin', 'moderator') DEFAULT 'admin',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                major VARCHAR(100),
                academic_year VARCHAR(50),
                gmu_id VARCHAR(20) UNIQUE,
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                role ENUM('student', 'member', 'executive') DEFAULT 'student',
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
            """
        ]
        
        try:
            for table_sql in tables_sql:
                cursor.execute(table_sql)
            
            # Insert default admin users
            cursor.execute("SELECT COUNT(*) FROM admin_users")
            if cursor.fetchone()[0] == 0:
                admin_users = [
                    ('superadmin', 'superadmin123', 'superadmin@gmucodingclub.com', 'Super Administrator', 'super_admin'),
                    ('admin', 'admin123', 'admin@gmucodingclub.com', 'Club Administrator', 'admin'),
                    ('events_manager', 'events123', 'events@gmucodingclub.com', 'Events Manager', 'moderator'),
                    ('projects_manager', 'projects123', 'projects@gmucodingclub.com', 'Projects Coordinator', 'moderator')
                ]
                for username, password, email, full_name, role in admin_users:
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    cursor.execute(
                        "INSERT INTO admin_users (username, password_hash, email, full_name, role) VALUES (%s, %s, %s, %s, %s)",
                        (username, password_hash, email, full_name, role)
                    )
            
            # Insert sample student users
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                student_users = [
                    ('john_doe', 'student123', 'jdoe@gmu.edu', 'John Doe', 'Computer Science', 'Junior', 'G12345678', 'student'),
                    ('jane_smith', 'student123', 'jsmith@gmu.edu', 'Jane Smith', 'Software Engineering', 'Senior', 'G12345679', 'member'),
                    ('mike_wilson', 'student123', 'mwilson@gmu.edu', 'Mike Wilson', 'Data Science', 'Sophomore', 'G12345680', 'executive')
                ]
                for username, password, email, full_name, major, year, gmu_id, role in student_users:
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    cursor.execute(
                        "INSERT INTO users (username, password_hash, email, full_name, major, academic_year, gmu_id, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (username, password_hash, email, full_name, major, year, gmu_id, role)
                    )
            
            # Insert sample events
            cursor.execute("SELECT COUNT(*) FROM events")
            if cursor.fetchone()[0] == 0:
                sample_events = [
                    ('Web Development Workshop', '2024-03-20', '14:00:00', 'GMU Engineering Building', 'Learn modern web development with React and Flask', 'Workshop', 30, 2),
                    ('Hackathon 2024', '2024-03-15', '10:00:00', 'GMU Innovation Hall', '24-hour coding competition with amazing prizes!', 'Hackathon', 50, 1),
                    ('AI & Machine Learning Seminar', '2024-04-05', '15:00:00', 'GMU Research Hall', 'Introduction to AI and ML concepts', 'Workshop', 40, 3)
                ]
                for event in sample_events:
                    cursor.execute(
                        "INSERT INTO events (title, date, time, location, description, category, max_participants, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        event
                    )
            
            # Insert sample projects
            cursor.execute("SELECT COUNT(*) FROM projects")
            if cursor.fetchone()[0] == 0:
                sample_projects = [
                    ('Campus Navigation App', 'A mobile app to help students navigate GMU campus', '["React Native", "Firebase", "Google Maps API"]', 'Mobile', 'https://github.com/gmucoding/campus-nav', 4),
                    ('AI Study Assistant', 'AI-powered tool to help students with studying', '["Python", "TensorFlow", "Flask"]', 'AI/ML', 'https://github.com/gmucoding/ai-study-assistant', 2),
                    ('Club Website', 'Official website for GMU Coding Club', '["HTML/CSS", "JavaScript", "Flask", "MySQL"]', 'Web', 'https://github.com/gmucoding/club-website', 1)
                ]
                for project in sample_projects:
                    cursor.execute(
                        "INSERT INTO projects (title, description, technologies, category, github_url, created_by) VALUES (%s, %s, %s, %s, %s, %s)",
                        project
                    )
            
            connection.commit()
            print("✅ Database initialized successfully!")
            return True
            
        except Error as e:
            print(f"❌ Error initializing database: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def get_all_events(self, active_only=True):
        connection = self.get_connection()
        if connection is None:
            return []
        
        cursor = connection.cursor(dictionary=True)
        try:
            if active_only:
                cursor.execute("SELECT * FROM events WHERE is_active = TRUE ORDER BY date, time")
            else:
                cursor.execute("SELECT * FROM events ORDER BY date, time")
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting events: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    def get_event_by_id(self, event_id):
        connection = self.get_connection()
        if connection is None:
            return None
        
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting event: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def add_event(self, event_data):
        connection = self.get_connection()
        if connection is None:
            return False
        
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO events (title, date, time, location, description, category, max_participants)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                event_data['title'],
                event_data['date'],
                event_data['time'],
                event_data['location'],
                event_data['description'],
                event_data['category'],
                event_data['max_participants']
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding event: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def update_event_status(self, event_id, is_active):
        connection = self.get_connection()
        if connection is None:
            return False
        
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE events SET is_active = %s WHERE id = %s", (is_active, event_id))
            connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error updating event status: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def delete_event(self, event_id):
        connection = self.get_connection()
        if connection is None:
            return False
        
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
            connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting event: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def register_for_event(self, event_id, registration_data):
        connection = self.get_connection()
        if connection is None:
            return False, "Database connection failed"
        
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT max_participants, current_participants FROM events WHERE id = %s AND is_active = TRUE", (event_id,))
            event = cursor.fetchone()
            
            if not event:
                return False, "Event not found or not active"
            
            max_participants, current_participants = event
            if current_participants >= max_participants:
                return False, "Event is full"
            
            cursor.execute("SELECT id FROM event_registrations WHERE event_id = %s AND email = %s", (event_id, registration_data['email']))
            if cursor.fetchone():
                return False, "Already registered for this event"
            
            cursor.execute("""
                INSERT INTO event_registrations (event_id, name, email, major, academic_year)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                event_id,
                registration_data['name'],
                registration_data['email'],
                registration_data.get('major'),
                registration_data.get('year')
            ))
            
            cursor.execute("UPDATE events SET current_participants = current_participants + 1 WHERE id = %s", (event_id,))
            
            connection.commit()
            return True, "Registration successful"
            
        except Error as e:
            print(f"Error registering for event: {e}")
            return False, "Registration failed"
        finally:
            cursor.close()
            connection.close()
    
    def get_event_registrations(self, event_id=None):
        connection = self.get_connection()
        if connection is None:
            return []
        
        cursor = connection.cursor(dictionary=True)
        try:
            if event_id:
                cursor.execute("""
                    SELECT er.*, e.title as event_title 
                    FROM event_registrations er 
                    JOIN events e ON er.event_id = e.id 
                    WHERE er.event_id = %s 
                    ORDER BY er.registration_date DESC
                """, (event_id,))
            else:
                cursor.execute("""
                    SELECT er.*, e.title as event_title 
                    FROM event_registrations er 
                    JOIN events e ON er.event_id = e.id 
                    ORDER BY er.registration_date DESC
                """)
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting registrations: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    def add_club_member(self, member_data):
        connection = self.get_connection()
        if connection is None:
            return False
        
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO club_members (name, email, major, academic_year, interests, experience_level, message, newsletter_subscription)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                member_data['name'],
                member_data['email'],
                member_data.get('major'),
                member_data.get('year'),
                member_data.get('interest'),
                member_data.get('experience'),
                member_data.get('message'),
                member_data.get('newsletter', True)
            ))
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding member: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def get_all_projects(self, category='all'):
        connection = self.get_connection()
        if connection is None:
            return []
        
        cursor = connection.cursor(dictionary=True)
        try:
            if category == 'all':
                cursor.execute("SELECT * FROM projects WHERE is_active = TRUE ORDER BY created_at DESC")
            else:
                cursor.execute("SELECT * FROM projects WHERE category = %s AND is_active = TRUE ORDER BY created_at DESC", (category,))
            
            projects = cursor.fetchall()
            for project in projects:
                if project['technologies']:
                    try:
                        project['technologies'] = json.loads(project['technologies'])
                    except:
                        project['technologies'] = []
            return projects
        except Error as e:
            print(f"Error getting projects: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    def get_project_categories(self):
        connection = self.get_connection()
        if connection is None:
            return []
        
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT DISTINCT category FROM projects WHERE is_active = TRUE")
            return [row[0] for row in cursor.fetchall()]
        except Error as e:
            print(f"Error getting categories: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    def verify_admin(self, username, password):
        connection = self.get_connection()
        if connection is None:
            return None
        
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, username, email, full_name, role, password_hash FROM admin_users WHERE username = %s AND is_active = TRUE", (username,))
            result = cursor.fetchone()
            
            if result:
                input_hash = hashlib.sha256(password.encode()).hexdigest()
                if input_hash == result['password_hash']:
                    cursor.execute("UPDATE admin_users SET last_login = CURRENT_TIMESTAMP WHERE id = %s", (result['id'],))
                    connection.commit()
                    return result
            return None
        except Error as e:
            print(f"Error verifying admin: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def create_user(self, user_data):
        connection = self.get_connection()
        if connection is None:
            return False, "Database connection failed"
        
        cursor = connection.cursor()
        try:
            password_hash = hashlib.sha256(user_data['password'].encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, full_name, major, academic_year, gmu_id, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_data['username'],
                password_hash,
                user_data['email'],
                user_data['full_name'],
                user_data.get('major'),
                user_data.get('academic_year'),
                user_data.get('gmu_id'),
                user_data.get('role', 'student')
            ))
            connection.commit()
            return True, "User created successfully"
        except Error as e:
            print(f"Error creating user: {e}")
            return False, "Username or email already exists"
        finally:
            cursor.close()
            connection.close()
    
    def verify_user(self, username, password):
        connection = self.get_connection()
        if connection is None:
            return None
        
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, username, email, full_name, role, password_hash 
                FROM users 
                WHERE username = %s AND is_active = TRUE
            """, (username,))
            result = cursor.fetchone()
            
            if result:
                input_hash = hashlib.sha256(password.encode()).hexdigest()
                if input_hash == result['password_hash']:
                    cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s", (result['id'],))
                    connection.commit()
                    return result
            return None
        except Error as e:
            print(f"Error verifying user: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def get_user_by_id(self, user_id):
        connection = self.get_connection()
        if connection is None:
            return None
        
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, username, email, full_name, major, academic_year, role FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def get_all_admins(self):
        connection = self.get_connection()
        if connection is None:
            return []
        
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, username, email, full_name, role, is_active, created_at FROM admin_users ORDER BY created_at DESC")
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting admins: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    def create_admin_user(self, admin_data):
        connection = self.get_connection()
        if connection is None:
            return False, "Database connection failed"
        
        cursor = connection.cursor()
        try:
            password_hash = hashlib.sha256(admin_data['password'].encode()).hexdigest()
            cursor.execute("""
                INSERT INTO admin_users (username, password_hash, email, full_name, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                admin_data['username'],
                password_hash,
                admin_data['email'],
                admin_data['full_name'],
                admin_data.get('role', 'admin')
            ))
            connection.commit()
            return True, "Admin user created successfully"
        except Error as e:
            print(f"Error creating admin: {e}")
            return False, "Username or email already exists"
        finally:
            cursor.close()
            connection.close()

db = Database()