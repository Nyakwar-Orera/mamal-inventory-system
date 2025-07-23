from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Asset, Maintenance
from app.maintenance import bp
from app.maintenance.forms import MaintenanceForm, MaintenanceUpdateForm

@bp.route('/')
@login_required
def view_maintenance():
    status = request.args.get('status', 'Pending', type=str)
    maintenance_list = Maintenance.query.filter_by(status=status)\
        .order_by(Maintenance.start_date.desc()).all()
    return render_template('maintenance/view_maintenance.html', 
                         maintenance_list=maintenance_list,
                         current_status=status)

@bp.route('/add/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def add_maintenance(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    form = MaintenanceForm()
    
    if form.validate_on_submit():
        maintenance = Maintenance(
            asset_id=asset_id,
            description=form.description.data,
            cost=form.cost.data,
            technician=form.technician.data,
            status=form.status.data
        )
        asset.status = 'Maintenance'
        db.session.add(maintenance)
        db.session.commit()
        flash('Maintenance record added successfully!', 'success')
        return redirect(url_for('maintenance.view_maintenance'))
    
    return render_template('maintenance/add_maintenance.html', form=form, asset=asset)

@bp.route('/update/<int:maintenance_id>', methods=['GET', 'POST'])
@login_required
def update_maintenance(maintenance_id):
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    asset = maintenance.asset
    form = MaintenanceUpdateForm(obj=maintenance)
    
    if form.validate_on_submit():
        maintenance.description = form.description.data
        maintenance.cost = form.cost.data
        maintenance.technician = form.technician.data
        maintenance.status = form.status.data
        
        if form.status.data == 'Completed':
            maintenance.end_date = datetime.utcnow()
            asset.status = 'Available'
        elif form.status.data in ['Pending', 'In Progress']:
            asset.status = 'Maintenance'
        
        db.session.commit()
        flash('Maintenance record updated successfully!', 'success')
        return redirect(url_for('maintenance.view_maintenance'))
    
    return render_template('maintenance/update_maintenance.html', form=form, maintenance=maintenance)

@bp.route('/complete/<int:maintenance_id>', methods=['POST'])
@login_required
def complete_maintenance(maintenance_id):
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    maintenance.status = 'Completed'
    maintenance.end_date = datetime.utcnow()
    maintenance.asset.status = 'Available'
    db.session.commit()
    flash('Maintenance marked as completed!', 'success')
    return redirect(url_for('maintenance.view_maintenance'))