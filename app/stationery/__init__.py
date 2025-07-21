# app/stationery/__init__.py

from flask import Blueprint

bp = Blueprint('stationery', __name__)

from app.stationery import routes  # Import routes after the blueprint is created
