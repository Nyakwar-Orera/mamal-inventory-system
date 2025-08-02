from flask import (
    render_template, request, jsonify, url_for, redirect,
    make_response, current_app
)
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Asset, Stationery, Maintenance, Checkout
from app.email import send_dashboard_report_email
from io import StringIO
import csv

# ----------------------------
# Root & Info Routes
# ----------------------------

@bp.route('/')
def index():
    """Redirect authenticated users to dashboard; show landing for others."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/index.html')

@bp.route('/info')
def info():
    """Optional info route."""
    return "Welcome to MAMAL Inventory System"

# ----------------------------
# Dashboard Route
# ----------------------------

@bp.route('/dashboard')
@login_required
def dashboard():
    """Render the main dashboard with asset summaries."""

    asset_counts = {
    'monitor': Asset.query.filter_by(asset_type='Monitor').count(),
    'keyboard': Asset.query.filter_by(asset_type='Keyboard').count(),
    'cpu': Asset.query.filter_by(asset_type='CPU').count(),
    'mouse': Asset.query.filter_by(asset_type='Mouse').count(),
    'printer': Asset.query.filter_by(asset_type='Printer').count(),  # ✅ add this
    'server': Asset.query.filter_by(asset_type='Server').count(),    # ✅ add this
    'other': Asset.query.filter(
        Asset.asset_type.notin_([
            'Monitor', 'Keyboard', 'CPU', 'Mouse', 'Printer', 'Server'
        ])
    ).count()
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

    return render_template(
        'pages/dashboard.html',
        asset_counts=asset_counts,
        status_counts=status_counts,
        low_stock=low_stock,
        pending_maintenance=pending_maintenance,
        active_checkouts=active_checkouts
    )


# ----------------------------
# QR Code Scanner API
# ----------------------------

@bp.route('/scan_qr', methods=['POST'])
@login_required
def scan_qr():
    """Scan and decode asset information from QR code data."""
    data = request.get_json()
    if not data or 'qr_data' not in data:
        return jsonify({'error': 'Invalid QR data'}), 400

    try:
        # Parse QR string into key-value pairs
        asset_info = {}
        for line in data['qr_data'].split('\n'):
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
        current_app.logger.error(f"QR scan error: {str(e)}")
        return jsonify({'error': 'Server error during QR scan'}), 500

# ----------------------------
# Email Dashboard Report
# ----------------------------

@bp.route('/send-dashboard-email', methods=['POST'])
@login_required
def send_dashboard_email_route():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'success': False, 'error': 'Email is required'}), 400

    try:
        email = data['email']

        asset_counts = {
            'monitor': Asset.query.filter_by(asset_type='Monitor').count(),
            'keyboard': Asset.query.filter_by(asset_type='Keyboard').count(),
            'cpu': Asset.query.filter_by(asset_type='CPU').count(),
            'mouse': Asset.query.filter_by(asset_type='Mouse').count(),
            'printer': Asset.query.filter_by(asset_type='Printer').count(),
            'server': Asset.query.filter_by(asset_type='Server').count(),
            'other': Asset.query.filter(
                Asset.asset_type.notin_([
                    'Monitor', 'Keyboard', 'CPU', 'Mouse', 'Printer', 'Server'
                ])
            ).count()
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

        send_dashboard_report_email(
            asset_counts,
            status_counts,
            low_stock,
            pending_maintenance,
            active_checkouts,
            recipient=email
        )

        return jsonify({'success': True})

    except Exception as e:
        current_app.logger.error(f"Email sending failed: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to send report'}), 500

# ----------------------------
# Export Dashboard as CSV
# ----------------------------

@bp.route('/export-dashboard')
@login_required
def export_dashboard():
    try:
        asset_counts = {
            'monitor': Asset.query.filter_by(asset_type='Monitor').count(),
            'keyboard': Asset.query.filter_by(asset_type='Keyboard').count(),
            'cpu': Asset.query.filter_by(asset_type='CPU').count(),
            'mouse': Asset.query.filter_by(asset_type='Mouse').count(),
            'printer': Asset.query.filter_by(asset_type='Printer').count(),
            'server': Asset.query.filter_by(asset_type='Server').count(),
            'other': Asset.query.filter(
                Asset.asset_type.notin_([
                    'Monitor', 'Keyboard', 'CPU', 'Mouse', 'Printer', 'Server'
                ])
            ).count()
        }

        status_counts = {
            'Available': Asset.query.filter_by(status='Available').count(),
            'In-use': Asset.query.filter_by(status='In-use').count(),
            'Maintenance': Asset.query.filter_by(status='Maintenance').count(),
            'Out of Service': Asset.query.filter_by(status='Out of Service').count()
        }

        pending_maintenance = Maintenance.query.filter_by(status='Pending').count()
        active_checkouts = Checkout.query.filter(Checkout.actual_return == None).count()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Section', 'Category', 'Count'])

        for category, count in asset_counts.items():
            writer.writerow(['Asset Type', category.title(), count])

        for status, count in status_counts.items():
            writer.writerow(['Status', status, count])

        writer.writerow(['Other', 'Pending Maintenance', pending_maintenance])
        writer.writerow(['Other', 'Active Checkouts', active_checkouts])

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=dashboard_report.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

    except Exception as e:
        current_app.logger.error(f"CSV export failed: {str(e)}")
        return "Export failed", 500

