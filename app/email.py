from flask_mail import Message
from flask import render_template, current_app
from app import mail
from threading import Thread

def send_async_email(app, msg):
    """Send email asynchronously within app context."""
    try:
        with app.app_context():
            mail.send(msg)
    except Exception as e:
        app.logger.error(f"Failed to send email: {e}")

def send_email(subject, sender, recipients, text_body, html_body):
    """Generic async email sender with text and HTML content."""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    # Use app context correctly for threading
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()

def send_password_reset_email(user):
    """Send password reset email to user with token."""
    token = user.get_reset_password_token()

    send_email(
        subject='[MamalLab] Reset Your Password',
        sender=current_app.config.get('MAIL_USERNAME'),
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token)
    )

def send_dashboard_report_email(asset_counts, status_counts, low_stock, pending_maintenance, active_checkouts, recipient=None):
    """Send dashboard summary email to admins or specified recipient."""
    subject = "Dashboard Report - Mamal Lab"
    sender = current_app.config.get('MAIL_USERNAME')

    recipients = [recipient] if recipient else current_app.config.get('ADMINS', [])

    if not recipients:
        current_app.logger.warning("No recipients configured for dashboard email.")
        return

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
