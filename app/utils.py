from flask import current_app, render_template
from flask_mail import Message
from app import mail
from app.models import Stationery
from threading import Thread
import qrcode
from io import BytesIO
import base64

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_dashboard_report_email(asset_counts, status_counts, low_stock, pending_maintenance, active_checkouts):
    subject = "Dashboard Report - Mamal Lab"
    sender = current_app.config['MAIL_USERNAME']
    recipients = current_app.config.get('ADMINS', [])

    if not recipients:
        raise RuntimeError("ADMIN_EMAIL not configured. Please set in .env or Config.")

    text_body = render_template(
        'email/dashboard_report.txt',
        asset_counts=asset_counts,
        status_counts=status_counts,
        low_stock=low_stock,
        pending_maintenance=pending_maintenance,
        active_checkouts=active_checkouts
    )

    html_body = render_template(
        'email/dashboard_report.html',
        asset_counts=asset_counts,
        status_counts=status_counts,
        low_stock=low_stock,
        pending_maintenance=pending_maintenance,
        active_checkouts=active_checkouts
    )

    send_email(subject, sender, recipients, text_body, html_body)

def check_low_stock(app):
    with app.app_context():
        low_stock_items = Stationery.query.filter(
            Stationery.quantity < Stationery.threshold
        ).all()

        if low_stock_items:
            subject = "Low Stock Alert - Mamal Lab"
            sender = current_app.config['MAIL_USERNAME']
            recipients = current_app.config.get('ADMINS', [])

            text_body = "The following stationery items are low on stock:\n\n"
            html_body = "<h2>Low Stock Alert</h2><ul>"

            for item in low_stock_items:
                text_body += f"{item.item_type}: {item.quantity} {item.unit} remaining (Threshold: {item.threshold})\n"
                html_body += f"<li>{item.item_type}: {item.quantity} {item.unit} remaining (Threshold: {item.threshold})</li>"

            html_body += "</ul>"

            send_email(subject, sender, recipients, text_body, html_body)

def generate_qr_code(asset_id, asset_name, serial_number):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    data = f"Asset ID: {asset_id}\nName: {asset_name}\nSerial: {serial_number}"
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"
