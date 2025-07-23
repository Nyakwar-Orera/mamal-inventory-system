import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()

def create_app(config_class=Config):
    # Remove the template_folder argument here:
    app = Flask(__name__)  
    app.config.from_object(config_class)

    # Use DATABASE_URL from environment if available
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', app.config['SQLALCHEMY_DATABASE_URI'])

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

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

    # Optional: print where Flask is looking for templates (debugging)
    print("Templates search path:", app.jinja_loader.searchpath)

    return app
