from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Asset
from app.assets import bp
from app.assets.forms import AssetFilterForm, AssetForm
import uuid

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

    # Fetch components for dropdowns
    components = {
        'monitor': Asset.query.filter_by(asset_type='monitor', parent_id=None).all(),
        'keyboard': Asset.query.filter_by(asset_type='keyboard', parent_id=None).all(),
        'mouse': Asset.query.filter_by(asset_type='mouse', parent_id=None).all(),
        'cpu': Asset.query.filter_by(asset_type='cpu', parent_id=None).all(),
    }

    if form.validate_on_submit():
        asset = Asset(
            name=form.name.data,
            serial_number=form.serial_number.data,
            asset_type=form.asset_type.data,
            purchase_date=form.purchase_date.data,
            purchase_cost=form.purchase_cost.data,
            location=form.location.data,
            status=form.status.data,
            condition=form.condition.data,
            notes=form.notes.data
        )
        db.session.add(asset)
        db.session.commit()

        asset.qr_code = str(uuid.uuid4())
        db.session.commit()

        # Handle components if desktop or laptop
        if asset.asset_type in ['desktop', 'laptop']:
            mode = request.form.get('component_mode', 'manual')

            if mode == 'manual':
                # Validate missing fields
                missing = []
                if not form.monitor_serial.data.strip():
                    missing.append('Monitor Serial Number')
                if not form.keyboard_serial.data.strip():
                    missing.append('Keyboard Serial Number')
                if not form.mouse_serial.data.strip():
                    missing.append('Mouse Serial Number')
                if not form.cpu_serial.data.strip():
                    missing.append('CPU Serial Number')

                if missing:
                    for field in missing:
                        flash(f"{field} is required for {asset.asset_type.capitalize()}.", "danger")
                    return render_template('assets/add_asset.html', form=form, components=components)

                # Create component assets manually
                component_data = [
                    ('Monitor', 'monitor', form.monitor_serial.data),
                    ('Keyboard', 'keyboard', form.keyboard_serial.data),
                    ('Mouse', 'mouse', form.mouse_serial.data),
                    ('CPU', 'cpu', form.cpu_serial.data),
                ]
                for name, type_value, serial in component_data:
                    component = Asset(
                        name=f"{name} for {asset.name}",
                        serial_number=serial,
                        asset_type=type_value,
                        purchase_date=form.purchase_date.data,
                        purchase_cost=0.0,
                        location=form.location.data,
                        status='Available',
                        condition='New',
                        notes=f"Component of {asset.name}",
                        parent_id=asset.id
                    )
                    db.session.add(component)

            elif mode == 'select':
                selected_ids = {
                    'monitor': request.form.get('monitor_id'),
                    'keyboard': request.form.get('keyboard_id'),
                    'mouse': request.form.get('mouse_id'),
                    'cpu': request.form.get('cpu_id'),
                }

                for comp_type, comp_id in selected_ids.items():
                    if comp_id:
                        component = Asset.query.get(int(comp_id))
                        if component and component.parent_id is None:
                            component.parent_id = asset.id
                            component.notes = f"Component of {asset.name}"
                            db.session.add(component)

        db.session.commit()
        flash('Asset added successfully!', 'success')
        return redirect(url_for('assets.view_assets'))

    return render_template('assets/add_asset.html', form=form, components=components)

@bp.route('/edit/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    form = AssetForm(obj=asset)
    if form.validate_on_submit():
        form.populate_obj(asset)
        asset.qr_code = str(uuid.uuid4())
        db.session.commit()
        flash('Asset updated successfully!', 'success')
        return redirect(url_for('assets.asset_details', asset_id=asset.id))
    return render_template('assets/edit_asset.html', form=form, asset=asset)

@bp.route('/delete/<int:asset_id>', methods=['POST'])
@login_required
def delete_asset(asset_id):
    if current_user.role != 'admin':
        flash('You do not have permission to delete assets.', 'danger')
        return redirect(url_for('assets.view_assets'))

    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    flash('Asset deleted successfully.', 'success')
    return redirect(url_for('assets.view_assets'))
