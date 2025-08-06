from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt
from flask import current_app
from sqlalchemy import event

# -----------------------------
# User Model
# -----------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='staff')
    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    checkouts = db.relationship('Checkout', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

    def deactivate(self):
        self.is_active = False
        db.session.commit()
    
    def reactivate(self):
        self.is_active = True
        db.session.commit()

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

    @staticmethod
    def get_active_users():
        return User.query.filter_by(is_active=True).all()


# -----------------------------
# Asset Model
# -----------------------------
class Asset(db.Model):
    __tablename__ = 'asset'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    asset_type = db.Column(db.String(50), nullable=False, index=True)
    location = db.Column(db.String(50), index=True)
    status = db.Column(db.String(20), default='Available', index=True)
    condition = db.Column(db.String(100))
    notes = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=True)
    components = db.relationship(
        'Asset',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    maintenance = db.relationship('Maintenance', backref='asset', lazy='dynamic')
    checkouts = db.relationship('Checkout', backref='asset', lazy='dynamic')

    def __repr__(self):
        return f'<Asset {self.name} - {self.serial_number}>'

# Automatically update last_updated on asset changes
@event.listens_for(Asset, 'before_update')
def update_asset_timestamp(mapper, connection, target):
    target.last_updated = datetime.utcnow()


# -----------------------------
# AssetTransfer Model
# -----------------------------
class AssetTransfer(db.Model):
    __tablename__ = 'asset_transfer'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    from_location = db.Column(db.String(50), nullable=False)
    to_location = db.Column(db.String(50), nullable=False)
    transferred_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transfer_date = db.Column(db.DateTime, default=datetime.utcnow)

    asset = db.relationship('Asset', backref='transfers')
    user = db.relationship('User', backref='transfers')

    def __repr__(self):
        return f'<Transfer {self.asset.name} from {self.from_location} to {self.to_location}>'

# -----------------------------
# Stationery Model
# -----------------------------
class Stationery(db.Model):
    __tablename__ = 'stationery'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    item_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20), default='sheets')
    threshold = db.Column(db.Integer)
    location = db.Column(db.String(50), index=True)

    def __repr__(self):
        return f'<Stationery {self.item_type} - {self.quantity} {self.unit}>'

# Automatically update last_updated on stationery changes
@event.listens_for(Stationery, 'before_update')
def update_stationery_timestamp(mapper, connection, target):
    target.last_updated = datetime.utcnow()


# -----------------------------
# Maintenance Model
# -----------------------------
class Maintenance(db.Model):
    __tablename__ = 'maintenance'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    cost = db.Column(db.Float)
    technician = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pending')

    def __repr__(self):
        asset_name = self.asset.name if self.asset else "Unknown"
        return f'<Maintenance on {asset_name} by {self.technician}>'


# -----------------------------
# Checkout Model
# -----------------------------
class Checkout(db.Model):
    __tablename__ = 'checkout'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    checkout_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_return = db.Column(db.DateTime)
    actual_return = db.Column(db.DateTime)
    condition_out = db.Column(db.String(100))
    condition_in = db.Column(db.String(100))
    notes = db.Column(db.Text)

    def __repr__(self):
        asset_name = self.asset.name if self.asset else "Unknown"
        username = self.user.username if self.user else "Unknown"
        return f'<Checkout {asset_name} by {username}>'


# -----------------------------
# Flask-Login Integration
# -----------------------------
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
