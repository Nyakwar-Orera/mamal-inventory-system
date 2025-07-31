from flask import current_app, render_template
from flask_mail import Message
from app import mail
from app.models import Stationery
from threading import Thread

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
