from flask import Blueprint

bp = Blueprint('checkout', __name__, template_folder='templates')

# Import routes after blueprint creation to avoid circular imports
from app.checkout import routes
