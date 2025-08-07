from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_
from datetime import datetime

from app import db
from app.models import Asset, AssetTransfer
from app.assets import bp
from app.assets.forms import AssetForm, AssetFilterForm, TransferAssetForm

def flash_message(message, category='info'):
    flash(message, category)

@bp.route('/')
@login_required
def view_assets():
    page = request.args.get('page', 1, type=int)
    location = request.args.get('location', '', type=str)
    status = request.args.get('status', '', type=str)
    search = request.args.get('search', '', type=str)

    query = Asset.query

    if location:
        query = query.filter(Asset.location == location)
    if status:
        query = query.filter(Asset.status == status)
    if search:
        keyword = f"%{search}%"
        query = query.filter(
            or_(
                Asset.name.ilike(keyword),
                Asset.serial_number.ilike(keyword),
                Asset.asset_type.ilike(keyword),
                Asset.location.ilike(keyword),
            )
        )

    assets = query.order_by(Asset.name.asc()).paginate(
        page=page,
        per_page=current_app.config.get('ITEMS_PER_PAGE', 10)
    )

    filter_form = AssetFilterForm(location=location, status=status, search=search)
    return render_template('assets/view_assets.html', assets=assets, filter_form=filter_form)

@bp.route('/<int:asset_id>')
@login_required
def asset_details(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    return render_template('assets/asset_details.html', asset=asset)

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
        return redirect(url_for('assets.add_asset'))

    return render_template('assets/add_asset.html', form=form)

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

# -------------------------------
# ✅ Transfer Asset Feature
# -------------------------------
@bp.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer_asset():
    form = TransferAssetForm()
    form.asset_id.choices = [(a.id, f"{a.name} ({a.serial_number})") for a in Asset.query.order_by(Asset.name).all()]

    if form.validate_on_submit():
        asset = Asset.query.get_or_404(form.asset_id.data)
        from_location = asset.location
        to_location = form.to_location.data

        if from_location == to_location:
            flash_message("Asset is already in the selected location.", "warning")
        else:
            asset.location = to_location
            db.session.commit()

            transfer = AssetTransfer(
                asset_id=asset.id,
                from_location=from_location,
                to_location=to_location,
                transferred_by=current_user.id,
                transfer_date=datetime.utcnow()
            )
            db.session.add(transfer)
            db.session.commit()

            flash_message("Asset transferred successfully!", "success")
            return redirect(url_for('assets.transfer_asset'))

    return render_template('assets/transfer_asset.html', form=form)

@bp.route('/transfer-history')
@login_required
def transfer_history():
    page = request.args.get('page', 1, type=int)
    transfers = AssetTransfer.query.order_by(AssetTransfer.transfer_date.desc()).paginate(
        page=page,
        per_page=current_app.config.get('ITEMS_PER_PAGE', 10)
    )
    return render_template('assets/transfer_history.html', transfers=transfers)
