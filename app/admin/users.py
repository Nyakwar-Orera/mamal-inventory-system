from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import User
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin-only access check
def admin_only():
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('main.dashboard'))

@admin_bp.route('/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        return admin_only()

    users = User.query.all()  # Get all users
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return admin_only()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash('User has been added successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/add_user.html')

@admin_bp.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin':
        return admin_only()

    user = User.query.get(id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin.manage_users'))

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = request.form['role']

        if request.form['password']:
            user.set_password(request.form['password'])

        db.session.commit()
        flash('User details updated!', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/deactivate_user/<int:id>', methods=['GET'])
@login_required
def deactivate_user(id):
    if current_user.role != 'admin':
        return admin_only()

    user = User.query.get(id)
    if user:
        user.deactivate()
        flash(f'User {user.username} has been deactivated.', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/reactivate_user/<int:id>', methods=['GET'])
@login_required
def reactivate_user(id):
    if current_user.role != 'admin':
        return admin_only()

    user = User.query.get(id)
    if user:
        user.reactivate()
        flash(f'User {user.username} has been reactivated.', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('admin.manage_users'))
