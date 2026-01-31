"""
Database Seeding Script
=======================
This script initializes the database with the default admin user.

Usage:
    python seed.py              # Full reset (drops all tables)
    python seed.py --no-drop    # Add seed data without dropping

WARNING: Running without --no-drop will DELETE ALL EXISTING DATA!
"""

import sys
import bcrypt
from app import create_app, db
from app.models import User

def seed_database(drop_tables=True):
    app = create_app()
    
    with app.app_context():
        if drop_tables:
            print("⚠️  WARNING: Dropping all tables...")
            db.drop_all()
            print("✅ Tables dropped.")
        
        print("📦 Creating all tables...")
        db.create_all()
        print("✅ Tables created.")
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email='admin@joitex.com').first()
        if existing_admin:
            print("ℹ️  Admin user already exists. Skipping...")
            return
        
        print("👤 Creating admin user...")
        password = 'admin123'  # Default password - change in production!
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # All portals access for admin
        admin_portals = ['admin', 'callcenter', 'sales', 'salesexec', 'engineer', 'inventory', 'network', 'finance']
        
        admin = User(
            email='admin@joitex.com', 
            password_hash=hashed, 
            name='Admin User', 
            role='admin',
        )
        admin.permissions = ['all']
        admin.portals = admin_portals
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin user created successfully!")
        print("   Email: admin@joitex.com")
        print("   Password: admin123")
        print("\n⚠️  IMPORTANT: Change the admin password in production!")

if __name__ == '__main__':
    drop = '--no-drop' not in sys.argv
    seed_database(drop_tables=drop)
