from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Create new tables (like UserLog)
    db.create_all()
    print("Created new tables (if any).")

    # Add columns to User table
    # We use a transaction for the connection
    with db.engine.connect() as conn:
        trans = conn.begin()
        try:
            # Check if columns exist or just try to add them. 
            # SQLite will error if column exists, which we catch.
            
            columns = [
                ("last_login", "DATETIME"),
                ("last_logout", "DATETIME"),
                ("last_seen", "DATETIME"),
                ("is_active", "BOOLEAN DEFAULT 1")
            ]
            
            for col_name, col_type in columns:
                try:
                    conn.execute(text(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}"))
                    print(f"Added {col_name}")
                except Exception as e:
                    # Likely column already exists
                    print(f"Skipping {col_name}: {e}")
            
            trans.commit()
            print("Schema update complete.")
        except Exception as e:
            trans.rollback()
            print(f"Error during schema update: {e}")
