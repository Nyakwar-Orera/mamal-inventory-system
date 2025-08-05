from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
from app.email import send_low_stock_summary_email

scheduler = BackgroundScheduler()

def start_scheduler():
    # Schedule the low stock email alert to run every day at 9am (server time)
    scheduler.add_job(func=send_low_stock_summary_email, trigger='cron', hour=9, minute=0, id='low_stock_alert')

    scheduler.start()
    current_app.logger.info("APScheduler started with low stock alert job.")
