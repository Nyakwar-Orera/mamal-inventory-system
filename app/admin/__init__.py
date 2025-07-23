from flask import Blueprint

from .users import admin_bp

def register_admin_routes(app):
    app.register_blueprint(admin_bp)
