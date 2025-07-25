from app import create_app, db
from app.models import User, Asset, Stationery, Maintenance, Checkout

app = create_app()

@app.before_first_request
def initialize_database():
    # ⚠️ WARNING: This deletes everything!
    db.drop_all()
    db.create_all()
    print("✅ Database reset: all tables dropped and recreated.")

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
    app.run()
