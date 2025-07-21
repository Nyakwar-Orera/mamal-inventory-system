from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Asset, Stationery, Maintenance, Checkout
from app.admin.forms import AddUserForm, EditUserForm
from werkzeug.security import generate_password_hash
from functools import wraps
from app.utils import send_dashboard_report_email  # ← Import the email utility

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Only allow access to users with the 'admin' role
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash("You don't have permission to access this page", "danger")
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Manage Users
@bp.route('/manage_users')
@login_required
@admin_only
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

# Add User
@bp.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_only
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role=form.role.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("User added successfully!", "success")
        return redirect(url_for('admin.manage_users'))
    return render_template('admin/add_user.html', form=form)

# Edit User
@bp.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_user(id):
    user = User.query.get_or_404(id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash("User details updated successfully!", "success")
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/edit_user.html', form=form, user=user)

# Reactivate User
@bp.route('/reactivate_user/<int:id>')
@login_required
@admin_only
def reactivate_user(id):
    user = User.query.get_or_404(id)
    user.is_active = True
    db.session.commit()
    flash(f"User '{user.username}' has been reactivated.", "success")
    return redirect(url_for('admin.manage_users'))

# Deactivate User
@bp.route('/deactivate_user/<int:id>')
@login_required
@admin_only
def deactivate_user(id):
    user = User.query.get_or_404(id)
    if current_user.id == user.id:
        flash("You can't deactivate your own account.", "warning")
        return redirect(url_for('admin.manage_users'))
    user.is_active = False
    db.session.commit()
    flash(f"User '{user.username}' has been deactivated.", "info")
    return redirect(url_for('admin.manage_users'))

# ✅ Delete User
@bp.route('/delete_user/<int:id>', methods=['POST'])
@login_required
@admin_only
def delete_user(id):
    user = User.query.get_or_404(id)

    if current_user.id == user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for('admin.manage_users'))

    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user.username}' has been deleted.", "warning")
    return redirect(url_for('admin.manage_users'))

# ✅ Send Dashboard Report Email (AJAX endpoint)
@bp.route('/send-dashboard-email', methods=['POST'])
@login_required
@admin_only
def send_dashboard_email():
    try:
        # Collect asset type counts
        asset_counts = {
            'desktop': Asset.query.filter_by(asset_type='Desktop').count(),
            'printer': Asset.query.filter_by(asset_type='Printer').count(),
            'server': Asset.query.filter_by(asset_type='Server').count(),
            'other': Asset.query.filter(Asset.asset_type.notin_(['Desktop', 'Printer', 'Server'])).count()
        }

        # Collect status counts
        statuses = ['Available', 'In-use', 'Maintenance', 'Out of Service']
        status_counts = {status: Asset.query.filter_by(status=status).count() for status in statuses}

        # Low stock stationery
        low_stock = Stationery.query.filter(Stationery.quantity < Stationery.threshold).all()

        # Pending actions
        pending_maintenance = Maintenance.query.filter_by(status='Pending').count()
        active_checkouts = Checkout.query.filter_by(status='Checked Out').count()

        # Send email
        send_dashboard_report_email(
            asset_counts=asset_counts,
            status_counts=status_counts,
            low_stock=low_stock,
            pending_maintenance=pending_maintenance,
            active_checkouts=active_checkouts
        )

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
