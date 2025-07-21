from flask import render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required
from io import BytesIO
from datetime import datetime, timedelta
from app import db
from app.models import Asset, Stationery, Checkout, Maintenance
from app.reports import bp
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

@bp.route('/')
@login_required
def reports_dashboard():
    return render_template('reports/reports_dashboard.html')

@bp.route('/assets')
@login_required
def assets_report():
    assets = db.session.query(
        Asset.location,
        Asset.asset_type,
        db.func.count(Asset.id).label('count')
    ).group_by(Asset.location, Asset.asset_type).all()
    
    status_counts = db.session.query(
        Asset.status,
        db.func.count(Asset.id).label('count')
    ).group_by(Asset.status).all()
    
    return render_template('reports/assets_report.html',
                         assets=assets,
                         status_counts=status_counts)

@bp.route('/stationery')
@login_required
def stationery_report():
    stationery = Stationery.query.order_by(Stationery.item_type).all()
    return render_template('reports/stationery_report.html',
                         stationery=stationery)

@bp.route('/checkouts')
@login_required
def checkouts_report():
    time_period = request.args.get('period', 'month', type=str)
    
    if time_period == 'week':
        days = 7
    elif time_period == 'month':
        days = 30
    else:  # year
        days = 365
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    checkouts = Checkout.query.filter(
        Checkout.checkout_date >= start_date
    ).order_by(Checkout.checkout_date.desc()).all()
    
    return render_template('reports/checkouts_report.html',
                         checkouts=checkouts,
                         period=time_period)

@bp.route('/maintenance')
@login_required
def maintenance_report():
    maintenance = Maintenance.query.order_by(Maintenance.start_date.desc()).all()
    total_cost = sum(m.cost for m in maintenance if m.cost)
    return render_template('reports/maintenance_report.html',
                         maintenance=maintenance,
                         total_cost=total_cost)

# Export route for Excel and PDF (already present)
@bp.route('/export/<report_type>/<format>')
@login_required
def export_report(report_type, format):
    if report_type == 'assets':
        query = Asset.query
        filename = 'assets_report'
    elif report_type == 'stationery':
        query = Stationery.query
        filename = 'stationery_report'
    elif report_type == 'checkouts':
        query = Checkout.query
        filename = 'checkouts_report'
    elif report_type == 'maintenance':
        query = Maintenance.query
        filename = 'maintenance_report'
    else:
        flash('Invalid report type', 'danger')
        return redirect(url_for('reports.reports_dashboard'))
    
    if format == 'excel':
        df = pd.read_sql(query.statement, db.engine)
        output = BytesIO()
        
        # Using the 'with' statement to handle ExcelWriter
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        
        output.seek(0)  # Rewind the output stream before sending it
        return send_file(output, 
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True,
                        download_name=f'{filename}.xlsx')
    
    elif format == 'pdf':
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"{filename.replace('_', ' ').title()}", styles['Title']))
        
        data = []
        if report_type == 'assets':
            data.append(['ID', 'Name', 'Type', 'Location', 'Status'])
            for asset in query:
                data.append([asset.id, asset.name, asset.asset_type, asset.location, asset.status])
        elif report_type == 'stationery':
            data.append(['ID', 'Item Type', 'Quantity', 'Unit', 'Location'])
            for item in query:
                data.append([item.id, item.item_type, item.quantity, item.unit, item.location or 'N/A'])
        elif report_type == 'checkouts':
            data.append(['ID', 'Asset', 'User', 'Checkout Date', 'Return Date'])
            for checkout in query:
                data.append([checkout.id,
                             checkout.asset.name,
                             checkout.user.username,
                             checkout.checkout_date.strftime('%Y-%m-%d'),
                             checkout.actual_return.strftime('%Y-%m-%d') if checkout.actual_return else 'Not returned'])
        elif report_type == 'maintenance':
            data.append(['ID', 'Asset', 'Start Date', 'End Date', 'Status', 'Cost'])
            for maint in query:
                data.append([maint.id,
                             maint.asset.name,
                             maint.start_date.strftime('%Y-%m-%d'),
                             maint.end_date.strftime('%Y-%m-%d') if maint.end_date else 'Ongoing',
                             maint.status,
                             f"${maint.cost:.2f}" if maint.cost else 'N/A'])
        
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 0), (-1, 0), 14),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)
        
        doc.build(elements)
        buffer.seek(0)
        return send_file(buffer, 
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name=f'{filename}.pdf')
    
    flash('Invalid export format', 'danger')
    return redirect(url_for('reports.reports_dashboard'))
