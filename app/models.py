from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt
from flask import current_app

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='staff')  # Default role is 'staff'
    is_active = db.Column(db.Boolean, default=True)  # For soft deletion (active/inactive)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Set the password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check the password hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

    def deactivate(self):
        """Deactivate the user account (soft delete)."""
        self.is_active = False
        db.session.commit()
    
    def reactivate(self):
        """Reactivate a deactivated user account."""
        self.is_active = True
        db.session.commit()

    # Password reset methods
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except Exception:
            return None
        return User.query.get(id)


class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)
    purchase_date = db.Column(db.Date)
    purchase_cost = db.Column(db.Float)
    location = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Available')
    condition = db.Column(db.String(100))
    notes = db.Column(db.Text)
    qr_code = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    maintenance = db.relationship('Maintenance', backref='asset', lazy='dynamic')
    checkouts = db.relationship('Checkout', backref='asset', lazy='dynamic')

    def __repr__(self):
        return f'<Asset {self.name} - {self.serial_number}>'


class Stationery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20), default='sheets')
    threshold = db.Column(db.Integer)
    location = db.Column(db.String(50))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Stationery {self.item_type} - {self.quantity} {self.unit}>'


class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    cost = db.Column(db.Float)
    technician = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pending')

    def __repr__(self):
        return f'<Maintenance for Asset {self.asset_id}>'


class Checkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    checkout_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_return = db.Column(db.DateTime)
    actual_return = db.Column(db.DateTime)
    condition_out = db.Column(db.String(100))
    condition_in = db.Column(db.String(100))
    notes = db.Column(db.Text)

    user = db.relationship('User', backref='checkouts')

    def __repr__(self):
        return f'<Checkout {self.asset_id} by {self.user_id}>'

# User Loader function for Flask-Login
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
