"""
Database Schema Migration Script
=================================
This script handles database schema updates without losing data.
Use this when you need to add new columns or tables to an existing database.

Usage:
    python update_schema.py

This is a lightweight alternative to Alembic for simple migrations.
For complex projects, consider using Flask-Migrate with Alembic.
"""

from app import create_app, db
from sqlalchemy import text, inspect

def get_existing_columns(inspector, table_name):
    """Get list of existing column names for a table"""
    try:
        columns = inspector.get_columns(table_name)
        return [col['name'] for col in columns]
    except:
        return []

def add_column_if_not_exists(conn, table_name, column_name, column_type):
    """Safely add a column if it doesn't exist"""
    inspector = inspect(conn)
    existing_columns = get_existing_columns(inspector, table_name)
    
    if column_name in existing_columns:
        print(f"  ⏭️  {table_name}.{column_name} already exists")
        return False
    
    try:
        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
        print(f"  ✅ Added {table_name}.{column_name}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to add {table_name}.{column_name}: {e}")
        return False

def update_schema():
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting schema update...\n")
        
        # Step 1: Create any new tables
        print("📦 Creating new tables (if any)...")
        db.create_all()
        print("✅ Table creation complete.\n")
        
        # Step 2: Add new columns to existing tables
        print("📝 Adding new columns to existing tables...")
        
        with db.engine.connect() as conn:
            trans = conn.begin()
            try:
                # User table updates
                user_columns = [
                    ("last_login", "DATETIME"),
                    ("last_logout", "DATETIME"),
                    ("last_seen", "DATETIME"),
                    ("is_active", "BOOLEAN DEFAULT 1"),
                    ("created_at", "DATETIME"),
                    ("updated_at", "DATETIME"),
                ]
                
                print("\n📋 User table:")
                for col_name, col_type in user_columns:
                    add_column_if_not_exists(conn, 'user', col_name, col_type)
                
                # Network devices table updates
                network_columns = [
                    ("model", "VARCHAR(100)"),
                    ("firmware_version", "VARCHAR(50)"),
                    ("last_heartbeat", "DATETIME"),
                ]
                
                print("\n📋 Network Devices table:")
                for col_name, col_type in network_columns:
                    add_column_if_not_exists(conn, 'network_devices', col_name, col_type)
                
                # Device logs table (if needed)
                # This should be created by db.create_all() but just in case
                
                trans.commit()
                print("\n✅ Schema update complete!")
                
            except Exception as e:
                trans.rollback()
                print(f"\n❌ Error during schema update: {e}")
                raise

def show_schema():
    """Display current database schema"""
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("\n📊 Current Database Schema")
        print("=" * 50)
        
        for table in tables:
            columns = inspector.get_columns(table)
            print(f"\n📋 {table}")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"   - {col['name']}: {col['type']} {nullable}")

if __name__ == '__main__':
    import sys
    
    if '--show' in sys.argv:
        show_schema()
    else:
        update_schema()
        if '--show' in sys.argv or '-s' in sys.argv:
            show_schema()
