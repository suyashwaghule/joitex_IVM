"""
Database Seeding Script
=======================
This script initializes the database with default data.

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

def create_demo_users():
    """Create demo users for all roles (development only)"""
    app = create_app()
    
    demo_users = [
        {'email': 'callcenter@joitex.com', 'password': 'call123', 'name': 'Call Center Agent', 'role': 'callcenter', 'portals': ['callcenter', 'sales']},
        {'email': 'sales@joitex.com', 'password': 'sales123', 'name': 'Sales Manager', 'role': 'sales', 'portals': ['sales', 'callcenter']},
        {'email': 'salesexec@joitex.com', 'password': 'exec123', 'name': 'Sales Executive', 'role': 'salesexec', 'portals': ['salesexec', 'sales']},
        {'email': 'engineer@joitex.com', 'password': 'eng123', 'name': 'Field Engineer', 'role': 'engineer', 'portals': ['engineer', 'inventory']},
        {'email': 'inventory@joitex.com', 'password': 'inv123', 'name': 'Inventory Manager', 'role': 'inventory', 'portals': ['inventory', 'engineer']},
        {'email': 'network@joitex.com', 'password': 'net123', 'name': 'Network Admin', 'role': 'network', 'portals': ['network', 'engineer']},
        {'email': 'finance@joitex.com', 'password': 'fin123', 'name': 'Finance Manager', 'role': 'finance', 'portals': ['finance', 'sales']},
    ]
    
    with app.app_context():
        for user_data in demo_users:
            existing = User.query.filter_by(email=user_data['email']).first()
            if existing:
                print(f"ℹ️  {user_data['email']} already exists. Skipping...")
                continue
            
            hashed = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user = User(
                email=user_data['email'],
                password_hash=hashed,
                name=user_data['name'],
                role=user_data['role']
            )
            user.portals = user_data['portals']
            user.permissions = []
            db.session.add(user)
            print(f"✅ Created {user_data['role']}: {user_data['email']}")
        
        db.session.commit()
        print("\n✅ Demo users created!")

if __name__ == '__main__':
    drop = '--no-drop' not in sys.argv
    demo = '--demo' in sys.argv
    
    seed_database(drop_tables=drop)
    
    if demo:
        print("\n📦 Creating demo users...")
        create_demo_users()
