import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate  # ✅ Added
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()  # ✅ Added
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()

# Import scheduler start function
from app.scheduler import start_scheduler

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ✅ Fix DATABASE_URL if on Render (ensure proper URI for SQLAlchemy)
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)  # ✅ Added
    login.init_app(app)
    mail.init_app(app)

    # Register Blueprints
    from app.main.routes import bp as main_bp
    from app.auth.routes import bp as auth_bp
    from app.assets.routes import bp as assets_bp
    from app.stationery.routes import bp as stationery_bp
    from app.checkout.routes import bp as checkout_bp
    from app.maintenance.routes import bp as maintenance_bp
    from app.reports.routes import bp as reports_bp
    from app.admin.routes import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(assets_bp, url_prefix='/assets')
    app.register_blueprint(stationery_bp, url_prefix='/stationery')
    app.register_blueprint(checkout_bp, url_prefix='/checkout')
    app.register_blueprint(maintenance_bp, url_prefix='/maintenance')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Start APScheduler after app context is pushed
    with app.app_context():
        start_scheduler()

    return app
