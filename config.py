import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///assets.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail Config
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Admin emails: supports multiple emails separated by commas in .env
    ADMINS = [email.strip() for email in os.environ.get('ADMIN_EMAIL', '').split(',') if email.strip()]

    # Pagination
    ITEMS_PER_PAGE = 20

    # Stock alert thresholds
    LOW_STOCK_THRESHOLD = {
        'A4': 100,
        'A3': 50,
        'A5': 50,
        'photo_paper': 20
    }
