from app import create_app, db

app = create_app()

ALTER_STATEMENTS = [
    # --- User table ---
    """ALTER TABLE "user" ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'staff';""",
    """ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;""",
    """ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP;""",

    # --- Asset table ---
    """ALTER TABLE asset ADD COLUMN IF NOT EXISTS purchase_date DATE;""",
    """ALTER TABLE asset ADD COLUMN IF NOT EXISTS purchase_cost FLOAT;""",
    """ALTER TABLE asset ADD COLUMN IF NOT EXISTS location VARCHAR(50);""",
    """ALTER TABLE asset ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'Available';""",
    """ALTER TABLE asset ADD COLUMN IF NOT EXISTS condition VARCHAR(100);""",
    """ALTER TABLE asset ADD COLUMN IF NOT EXISTS notes TEXT;""",
    """ALTER TABLE asset ADD COLUMN IF NOT EXISTS qr_code VARCHAR(100);""",
    """ALTER TABLE asset ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP;""",
    """ALTER TABLE asset ADD COLUMN IF NOT EXISTS parent_id INTEGER;""",
    """DO $$ BEGIN
        ALTER TABLE asset ADD CONSTRAINT fk_asset_parent FOREIGN KEY (parent_id) REFERENCES asset(id);
    EXCEPTION
        WHEN duplicate_object THEN NULL;
    END $$;""",

    # --- Stationery table ---
    """ALTER TABLE stationery ADD COLUMN IF NOT EXISTS unit VARCHAR(20) DEFAULT 'sheets';""",
    """ALTER TABLE stationery ADD COLUMN IF NOT EXISTS threshold INTEGER;""",
    """ALTER TABLE stationery ADD COLUMN IF NOT EXISTS location VARCHAR(50);""",
    """ALTER TABLE stationery ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP;""",

    # --- Maintenance table ---
    """ALTER TABLE maintenance ADD COLUMN IF NOT EXISTS start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;""",
    """ALTER TABLE maintenance ADD COLUMN IF NOT EXISTS end_date TIMESTAMP;""",
    """ALTER TABLE maintenance ADD COLUMN IF NOT EXISTS description TEXT;""",
    """ALTER TABLE maintenance ADD COLUMN IF NOT EXISTS cost FLOAT;""",
    """ALTER TABLE maintenance ADD COLUMN IF NOT EXISTS technician VARCHAR(100);""",
    """ALTER TABLE maintenance ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'Pending';""",

    # --- Checkout table ---
    """ALTER TABLE checkout ADD COLUMN IF NOT EXISTS checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;""",
    """ALTER TABLE checkout ADD COLUMN IF NOT EXISTS expected_return TIMESTAMP;""",
    """ALTER TABLE checkout ADD COLUMN IF NOT EXISTS actual_return TIMESTAMP;""",
    """ALTER TABLE checkout ADD COLUMN IF NOT EXISTS condition_out VARCHAR(100);""",
    """ALTER TABLE checkout ADD COLUMN IF NOT EXISTS condition_in VARCHAR(100);""",
    """ALTER TABLE checkout ADD COLUMN IF NOT EXISTS notes TEXT;"""
]

with app.app_context():
    for statement in ALTER_STATEMENTS:
        try:
            db.session.execute(statement)
        except Exception as e:
            print(f"Error executing: {statement}\n{e}")
    db.session.commit()
    print("✅ Database schema updated successfully.")
