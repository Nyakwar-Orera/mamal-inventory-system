from app import create_app, db
from app.models import User, Asset, Stationery, Maintenance, Checkout

app = create_app()

# ⚠️ TEMPORARY: Resetting the database (this will drop all tables and recreate them)
def reset_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ Database reset complete.")

reset_database()

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
