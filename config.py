import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-12345'
    
    # MySQL Database Configuration - Use environment variables
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'gmu_coding_club')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    
    # Event categories
    EVENT_CATEGORIES = ['Workshop', 'Competition', 'Social', 'Meeting', 'Hackathon']