from app import create_app, db
from app.models import User
import bcrypt

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()

    print("Creating admin user...")
    password = '123456789'
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Portals for admin (all access)
    admin_portals = ['admin', 'callcenter', 'sales', 'salesexec', 'engineer', 'inventory', 'network', 'finance']
    
    admin = User(
        email='admin@gmail.com', 
        password_hash=hashed, 
        name='Admin User', 
        role='admin',
    )
    # Set properties explicitly to ensure setters are called if constructor doesn't
    admin.permissions = ['all']
    admin.portals = admin_portals
    
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully.")
