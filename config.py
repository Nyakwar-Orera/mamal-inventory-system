import os
from dotenv import load_dotenv

# Load environment variables from .env if available
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///assets.db')
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Display name for sender in outgoing emails
    MAIL_DEFAULT_SENDER = (
        "Mamal Lab System",
        MAIL_USERNAME if MAIL_USERNAME else "no-reply@example.com"
    )

    # Admin email(s) - comma-separated in .env like: ADMIN_EMAIL=admin1@example.com,admin2@example.com
    ADMINS = [
        email.strip()
        for email in os.environ.get('ADMIN_EMAIL', '').split(',')
        if email.strip()
    ]

    # Pagination
    ITEMS_PER_PAGE = 20

    # Stock alert thresholds
    LOW_STOCK_THRESHOLD = {
        'A4': 5,
        'A3': 5,
        'A5': 5,
        'photo_paper': 10
    }
