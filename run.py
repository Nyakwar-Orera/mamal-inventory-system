from app import create_app, db
from app.models import User, Asset, Stationery, Maintenance, Checkout

app = create_app()

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
    app.run(debug=True, host='0.0.0.0', port=5000)

