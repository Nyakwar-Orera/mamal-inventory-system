from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Asset, Checkout, User
from app.checkout import bp
from app.checkout.forms import CheckoutForm, CheckinForm

# Route to view active checkouts
@bp.route('/active')
@login_required
def active_checkouts():
    checkouts = Checkout.query.filter_by(actual_return=None).order_by(Checkout.checkout_date.desc()).all()
    return render_template('checkout/active_checkouts.html', checkouts=checkouts)

# Route to view checkout history
@bp.route('/history')
@login_required
def checkout_history():
    page = request.args.get('page', 1, type=int)
    checkouts = Checkout.query.filter(Checkout.actual_return != None)\
        .order_by(Checkout.checkout_date.desc())\
        .paginate(page=page, per_page=current_app.config.get('ITEMS_PER_PAGE', 10))
    return render_template('checkout/checkout_history.html', checkouts=checkouts)

# Route to checkout an asset
@bp.route('/checkout/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def checkout_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)

    # Check if the asset is available for checkout
    if asset.status != 'Available':
        flash(f'This asset is not available for checkout (Status: {asset.status}).', 'danger')
        return redirect(url_for('assets.view_assets'))

    # Initialize the form
    form = CheckoutForm()
    form.asset_id.data = asset_id
    form.user_id.choices = [(u.id, u.username) for u in User.query.order_by(User.username).all()]

    # Check if there are no users available to checkout the asset
    if not form.user_id.choices:
        flash('No users available. Add users before checking out assets.', 'warning')
        return redirect(url_for('assets.view_assets'))

    # Handle the form submission
    if form.validate_on_submit():
        # Create a new checkout entry
        checkout = Checkout(
            asset_id=asset_id,
            user_id=form.user_id.data,
            expected_return=form.expected_return.data,
            condition_out=form.condition_out.data,
            notes=form.notes.data
        )
        
        # Update asset status to "In-use"
        asset.status = 'In-use'

        # Save the checkout and asset changes to the database
        db.session.add(checkout)
        db.session.commit()

        flash('Asset checked out successfully!', 'success')
        return redirect(url_for('checkout.active_checkouts'))

    return render_template('checkout/checkout_form.html', form=form, asset=asset)

# Route to check in an asset
@bp.route('/checkin/<int:checkout_id>', methods=['GET', 'POST'])
@login_required
def checkin_asset(checkout_id):
    # Retrieve the checkout and related asset
    checkout = Checkout.query.get_or_404(checkout_id)
    asset = checkout.asset

    # Ensure the asset has not already been checked in
    if checkout.actual_return:
        flash('This asset has already been checked in.', 'info')
        return redirect(url_for('checkout.active_checkouts'))

    # Initialize the check-in form
    form = CheckinForm(obj=checkout)

    # Handle form submission to update check-in details
    if form.validate_on_submit():
        checkout.actual_return = datetime.utcnow()  # Set the actual return date
        checkout.condition_in = form.condition_in.data  # Record the condition at check-in
        checkout.notes = form.notes.data  # Add any additional notes

        # Update asset status to "Available" after check-in
        asset.status = 'Available'

        # Commit the changes to the database
        db.session.commit()

        flash('Asset checked in successfully!', 'success')
        return redirect(url_for('checkout.active_checkouts'))

    return render_template('checkout/checkin_form.html', form=form, checkout=checkout)
