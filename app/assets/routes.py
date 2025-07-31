from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Asset
from app.assets import bp
from app.assets.forms import AssetFilterForm, AssetForm

# Flash wrapper for centralized message control
def flash_message(message, category='info'):
    flash(message, category)

# View all assets (with optional filtering)
@bp.route('/')
@login_required
def view_assets():
    page = request.args.get('page', 1, type=int)
    location = request.args.get('location', '', type=str)
    status = request.args.get('status', '', type=str)

    query = Asset.query
    if location:
        query = query.filter_by(location=location)
    if status:
        query = query.filter_by(status=status)

    assets = query.order_by(Asset.name.asc()).paginate(
        page=page,
        per_page=current_app.config.get('ITEMS_PER_PAGE', 10)
    )

    filter_form = AssetFilterForm(location=location, status=status)

    return render_template('assets/view_assets.html',
                           assets=assets,
                           filter_form=filter_form)

# View asset details
@bp.route('/<int:asset_id>')
@login_required
def asset_details(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    return render_template('assets/asset_details.html', asset=asset)

# Add a new asset
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_asset():
    form = AssetForm()
    if form.validate_on_submit():
        asset = Asset(
            name=form.name.data,
            serial_number=form.serial_number.data,
            asset_type=form.asset_type.data,
            location=form.location.data,
            status=form.status.data,
            condition=form.condition.data,
            notes=form.notes.data
        )
        db.session.add(asset)
        db.session.commit()

        flash_message('Asset added successfully!', 'success')
        return redirect(url_for('assets.view_assets'))

    return render_template('assets/add_asset.html', form=form)

# Edit existing asset
@bp.route('/edit/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    form = AssetForm(obj=asset)
    if form.validate_on_submit():
        form.populate_obj(asset)
        db.session.commit()
        flash_message('Asset updated successfully!', 'success')
        return redirect(url_for('assets.asset_details', asset_id=asset.id))
    return render_template('assets/edit_asset.html', form=form, asset=asset)

# Delete an asset
@bp.route('/delete/<int:asset_id>', methods=['POST'])
@login_required
def delete_asset(asset_id):
    if current_user.role != 'admin':
        flash_message('You do not have permission to delete assets.', 'danger')
        return redirect(url_for('assets.view_assets'))

    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    flash_message('Asset deleted successfully.', 'success')
    return redirect(url_for('assets.view_assets'))
