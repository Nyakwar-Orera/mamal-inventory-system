from app import create_app, db
from app.models import User, Asset, Stationery, Maintenance, Checkout

# Create and expose the app for gunicorn
app = create_app()

# Flask CLI shell context
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Asset': Asset,
        'Stationery': Stationery,
        'Maintenance': Maintenance,
        'Checkout': Checkout
    }

# Create tables if they don't exist (optional for prod, useful for dev)
with app.app_context():
    db.create_all()

# Only use this for local dev, not in production
# (gunicorn handles `app`)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
