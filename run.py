from app import create_app, db
from app.models import User, Asset, Stationery, Maintenance, Checkout

# Create the Flask app
app = create_app()

# Make shell context for Flask CLI
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

if __name__ == '__main__':
    # Create all tables if they do not exist
    with app.app_context():
        db.create_all()

    # Run the app on all network interfaces, port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
