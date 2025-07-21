from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Stationery
from app.stationery import bp  # Blueprint import (ensure this is correct)
from app.stationery.forms import StationeryForm, StationeryUpdateForm

# View all stationery items
@bp.route('/')
@login_required
def view_stationery():
    item_type = request.args.get('item_type')
    location = request.args.get('location')

    query = Stationery.query

    if item_type:
        query = query.filter_by(item_type=item_type)
    if location:
        query = query.filter_by(location=location)

    stationery_items = query.order_by(Stationery.item_type.asc()).all()
    return render_template('stationery/view_stationery.html', stationery_items=stationery_items)


# Add new stationery item
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_stationery():
    if current_user.role not in ['admin', 'staff']:
        flash('You do not have permission to add stationery.', 'danger')
        return redirect(url_for('stationery.view_stationery'))  # Ensure correct endpoint name
    
    form = StationeryForm()
    if form.validate_on_submit():
        stationery = Stationery(
            item_type=form.item_type.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            threshold=form.threshold.data,
            location=form.location.data
        )
        db.session.add(stationery)
        db.session.commit()
        flash('Stationery item added successfully!', 'success')
        return redirect(url_for('stationery.view_stationery'))  # Correct the URL to 'stationery.view_stationery'
    return render_template('stationery/add_stationery.html', form=form)

# Update an existing stationery item
@bp.route('/update/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_stationery(item_id):
    if current_user.role not in ['admin', 'staff']:
        flash('You do not have permission to update stationery.', 'danger')
        return redirect(url_for('stationery.view_stationery'))  # Correct redirect URL
    
    item = Stationery.query.get_or_404(item_id)
    form = StationeryUpdateForm(obj=item)
    
    if form.validate_on_submit():
        action = request.form.get('action')
        
        # Handle quantity changes based on user action
        if action == 'add':
            item.quantity += form.quantity_change.data
        elif action == 'subtract':
            item.quantity -= form.quantity_change.data
            if item.quantity < 0:
                item.quantity = 0
        
        # Update threshold and location if data is provided
        if form.threshold.data is not None:
            item.threshold = form.threshold.data
        if form.location.data:
            item.location = form.location.data
        
        db.session.commit()
        flash('Stationery item updated successfully!', 'success')
        return redirect(url_for('stationery.view_stationery'))  # Correct redirect URL
    
    return render_template('stationery/update_stationery.html', form=form, item=item)

# Delete a stationery item
@bp.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_stationery(item_id):
    if current_user.role != 'admin':
        flash('You do not have permission to delete stationery.', 'danger')
        return redirect(url_for('stationery.view_stationery'))  # Correct redirect URL
    
    item = Stationery.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Stationery item deleted successfully.', 'success')
    return redirect(url_for('stationery.view_stationery'))  # Correct redirect URL
