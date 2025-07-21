from flask import render_template, request, current_app, jsonify, url_for, redirect
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Asset, Stationery, Maintenance, Checkout
from app.email import send_dashboard_report_email

# Root route
@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/index.html')  # Landing page for unauthenticated users

# Info route (optional)
@bp.route('/info')
def info():
    return "Welcome to Mamal Lab Asset Management System"

# Dashboard route
@bp.route('/dashboard')
@login_required
def dashboard():
    asset_counts = {
        'desktop': Asset.query.filter_by(asset_type='desktop').count(),
        'printer': Asset.query.filter_by(asset_type='printer').count(),
        'server': Asset.query.filter_by(asset_type='server').count(),
        'other': Asset.query.filter(Asset.asset_type.notin_(['desktop', 'printer', 'server'])).count()
    }

    status_counts = {
        'Available': Asset.query.filter_by(status='Available').count(),
        'In-use': Asset.query.filter_by(status='In-use').count(),
        'Maintenance': Asset.query.filter_by(status='Maintenance').count(),
        'Out of Service': Asset.query.filter_by(status='Out of Service').count()
    }

    low_stock = Stationery.query.filter(
        Stationery.quantity < Stationery.threshold
    ).all()

    pending_maintenance = Maintenance.query.filter_by(status='Pending').count()
    active_checkouts = Checkout.query.filter(Checkout.actual_return == None).count()

    return render_template('pages/dashboard.html', 
                           asset_counts=asset_counts,
                           status_counts=status_counts,
                           low_stock=low_stock,
                           pending_maintenance=pending_maintenance,
                           active_checkouts=active_checkouts)

# QR code scanning route
@bp.route('/scan_qr', methods=['POST'])
@login_required
def scan_qr():
    data = request.get_json()
    if not data or 'qr_data' not in data:
        return jsonify({'error': 'Invalid QR data'}), 400

    try:
        qr_lines = data['qr_data'].split('\n')
        asset_info = {}
        for line in qr_lines:
            if ': ' in line:
                key, value = line.split(': ', 1)
                asset_info[key.strip().lower()] = value.strip()

        asset_id = int(asset_info.get('asset id', 0))
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404

        return jsonify({
            'id': asset.id,
            'name': asset.name,
            'serial_number': asset.serial_number,
            'type': asset.asset_type,
            'location': asset.location,
            'status': asset.status,
            'qr_code': asset.qr_code,
            'checkout_url': url_for('checkout.checkout_asset', asset_id=asset.id),
            'maintenance_url': url_for('maintenance.add_maintenance', asset_id=asset.id),
            'details_url': url_for('assets.asset_details', asset_id=asset.id)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New route to send dashboard email
@bp.route('/send-dashboard-email', methods=['POST'])
@login_required
def send_dashboard_email_route():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'success': False, 'error': 'Email is required'}), 400

    recipient_email = data['email']

    asset_counts = {
        'desktop': Asset.query.filter_by(asset_type='desktop').count(),
        'printer': Asset.query.filter_by(asset_type='printer').count(),
        'server': Asset.query.filter_by(asset_type='server').count(),
        'other': Asset.query.filter(Asset.asset_type.notin_(['desktop', 'printer', 'server'])).count()
    }

    status_counts = {
        'Available': Asset.query.filter_by(status='Available').count(),
        'In-use': Asset.query.filter_by(status='In-use').count(),
        'Maintenance': Asset.query.filter_by(status='Maintenance').count(),
        'Out of Service': Asset.query.filter_by(status='Out of Service').count()
    }

    low_stock = Stationery.query.filter(Stationery.quantity < Stationery.threshold).all()
    pending_maintenance = Maintenance.query.filter_by(status='Pending').count()
    active_checkouts = Checkout.query.filter(Checkout.actual_return == None).count()

    try:
        send_dashboard_report_email(
            asset_counts,
            status_counts,
            low_stock,
            pending_maintenance,
            active_checkouts,
            recipient=recipient_email
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
