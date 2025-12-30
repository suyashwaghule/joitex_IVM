from app import create_app, db
from app.models import User, Lead, OLT
from app.models_inquiry import Inquiry
from app.models_job import Job
from datetime import datetime, timedelta
import bcrypt

app = create_app()

DEMO_USERS = [
    { 
        "email": 'admin@joitex.com', 
        "password": 'admin123', 
        "role": 'admin', 
        "name": 'Admin User', 
        "permissions": ['all'],
        "portals": ['admin', 'callcenter', 'sales', 'salesexec', 'engineer', 'inventory', 'network', 'finance']
    },
    { 
        "email": 'callcenter@joitex.com', 
        "password": 'call123', 
        "role": 'callcenter', 
        "name": 'Call Center Agent', 
        "permissions": ['inquiries.create', 'inquiries.read', 'inquiries.update'],
        "portals": ['callcenter', 'sales']
    },
    { 
        "email": 'sales@joitex.com', 
        "password": 'sales123', 
        "role": 'sales', 
        "name": 'Sales Manager', 
        "permissions": ['inquiries.read', 'leads.all', 'activation.all'],
        "portals": ['sales', 'callcenter']
    },
    { 
        "email": 'salesexec@joitex.com', 
        "password": 'exec123', 
        "role": 'salesexec', 
        "name": 'Sales Executive', 
        "permissions": ['leads.create', 'leads.read', 'leads.update'],
        "portals": ['salesexec', 'sales']
    },
    { 
        "email": 'engineer@joitex.com', 
        "password": 'eng123', 
        "role": 'engineer', 
        "name": 'Field Engineer', 
        "permissions": ['jobs.read', 'jobs.update', 'devices.all'],
        "portals": ['engineer', 'inventory']
    },
    { 
        "email": 'inventory@joitex.com', 
        "password": 'inv123', 
        "role": 'inventory', 
        "name": 'Inventory Manager', 
        "permissions": ['inventory.all', 'vendors.all'],
        "portals": ['inventory', 'engineer']
    },
    { 
        "email": 'network@joitex.com', 
        "password": 'net123', 
        "role": 'network', 
        "name": 'Network Admin', 
        "permissions": ['olts.all', 'ipam.all', 'monitoring.all'],
        "portals": ['network', 'engineer']
    },
    { 
        "email": 'finance@joitex.com', 
        "password": 'fin123', 
        "role": 'finance', 
        "name": 'Finance Manager', 
        "permissions": ['licenses.all', 'billing.read', 'reports.financial'],
        "portals": ['finance', 'sales']
    }
]

def seed_users():
    with app.app_context():
        # db.drop_all() # Optional: reset db
        db.create_all()
        
        if User.query.first():
            print("Database already contains users.")
            # return # Uncomment to skip if exists, but for dev we might want to ensure they exist

        print("Seeding roles...")
        from app.models import Role
        # Extract unique roles from DEMO_USERS
        unique_roles = {}
        for u in DEMO_USERS:
            if u['role'] not in unique_roles:
                unique_roles[u['role']] = {
                    'name': u['role'],
                    'permissions': u['permissions'],
                    # Optional: Infer color or hardcode map
                }
        
        role_colors = {
            'admin': '#1976d2',
            'callcenter': '#0d9488',
            'sales': '#4f46e5',
            'salesexec': '#6366f1',
            'engineer': '#f97316',
            'inventory': '#9333ea',
            'network': '#16a34a',
            'finance': '#f59e0b'
        }

        for role_name, role_data in unique_roles.items():
            if not Role.query.filter_by(name=role_name).first():
                r = Role(
                    name=role_name,
                    description=f"System role for {role_name}",
                    color=role_colors.get(role_name, '#6c757d'),
                    permissions=role_data['permissions'],
                    is_system=True
                )
                db.session.add(r)
        db.session.commit()

        print("Seeding users...")
        for user_data in DEMO_USERS:
            if User.query.filter_by(email=user_data['email']).first():
                continue
                
            hashed = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            u = User(
                email=user_data['email'],
                password_hash=hashed,
                name=user_data['name'],
                role=user_data['role'], # This is a string field
                permissions=user_data['permissions'],
                portals=user_data['portals']
            )
            db.session.add(u)
        
        db.session.commit()
        
        # Seed extra data for charts if empty
        # Seed extra data for charts if empty
        if not Lead.query.first():
            print("Seeding Leads...")
            from datetime import timedelta
            now = datetime.utcnow()
            
            # Get sales exec user
            sales_exec = User.query.filter_by(role='salesexec').first()
            sales_exec_id = sales_exec.id if sales_exec else None

            # New Leads
            for i in range(10):
                db.session.add(Lead(
                    lead_number=f"L-2025-{100+i}",
                    name=f"Lead Customer {i}", 
                    status="new",
                    email=f"cust{i}@example.com",
                    phone=f"9876543{i:03d}",
                    address=f"Street {i}, Area {i}",
                    plan_interest="Fiber 100",
                    assigned_to=sales_exec_id,
                    follow_up_date=now + timedelta(days=(i % 3) - 1), # Some overdue, some today, some future
                    source="manual"
                ))
            
            # Feasibility Leads
            for i in range(5):
                 db.session.add(Lead(
                    lead_number=f"L-2025-{200+i}",
                    name=f"Lead Feasibility {i}", 
                    status="feasibility",
                    email=f"lead_feas{i}@example.com",
                    phone=f"9871111{i:03d}",
                    address=f"Feasibility Loc {i}",
                    plan_interest="Fiber 300",
                    assigned_to=sales_exec_id,
                    source="callcenter"
                 ))
            
            # Converted Leads (Status: installed)
            for i in range(8):
                 db.session.add(Lead(
                    lead_number=f"L-2025-{300+i}",
                    name=f"Converted User {i}", 
                    status="installed",
                    email=f"conv{i}@example.com",
                    phone=f"9872222{i:03d}",
                    address=f"Installation Loc {i}",
                    plan_interest="Fiber Ultra",
                    assigned_to=sales_exec_id,
                    updated_at=now - timedelta(days=i)
                 ))
            db.session.commit()

        from app.models_sales import BroadbandPlan
        if not BroadbandPlan.query.first():
            print("Seeding Plans...")
            plans = [
                BroadbandPlan(name="Fiber Starter", speed_mbps=50, price_monthly=499, data_limit_gb=0, description="Ideal for basic usage"),
                BroadbandPlan(name="Fiber Basic", speed_mbps=100, price_monthly=799, data_limit_gb=0, description="Great for streaming"),
                BroadbandPlan(name="Fiber Ultra", speed_mbps=300, price_monthly=1299, data_limit_gb=0, description="For power users & gaming"),
                BroadbandPlan(name="Fiber Gigabit", speed_mbps=1000, price_monthly=2499, data_limit_gb=0, description="Ultimate speed")
            ]
            db.session.add_all(plans)
            db.session.commit()

        if not OLT.query.first():
            print("Seeding OLTs...")
            db.session.add(OLT(name="OLT-South", status="online"))
            db.session.add(OLT(name="OLT-North", status="online"))
            db.session.add(OLT(name="OLT-West", status="offline"))
            db.session.commit()
            
        if not Inquiry.query.first():
            print("Seeding Inquiries...")
            db.session.add(Inquiry(
                inquiry_number="INQ-2024-001",
                customer_name="John Doe",
                phone="9876543210",
                service_type="home",
                address="123 Main St",
                status="pending"
            ))
            db.session.add(Inquiry(
                inquiry_number="INQ-2024-002",
                customer_name="Jane Smith",
                phone="8765432109",
                service_type="business",
                address="456 Tech Park",
                status="forwarded"
            ))
            db.session.commit()
            
            db.session.commit()
            
        if not Job.query.first():
            print("Seeding Jobs...")
            from datetime import timedelta, datetime
            now = datetime.utcnow()
            
            # Get engineer user
            engineer = User.query.filter_by(role='engineer').first()
            eng_id = engineer.id if engineer else None

            # Pending Installation
            db.session.add(Job(
                job_number="JOB-2025-001",
                customer_name="Rajesh Kumar",
                phone="9876543210",
                address="Plot 45, Andheri West",
                city="Mumbai",
                job_type="New Installation",
                plan="100 Mbps",
                priority="high",
                status="pending",
                scheduled_at=now + timedelta(hours=2),
                engineer_id=eng_id
            ))
            
            # In Progress Job
            db.session.add(Job(
                job_number="JOB-2025-002",
                customer_name="Priya Sharma",
                phone="9876543211",
                address="Tower B, Bandra Complex",
                city="Mumbai",
                job_type="Upgrade",
                plan="200 Mbps",
                priority="medium",
                status="in_progress",
                scheduled_at=now - timedelta(hours=1),
                started_at=now - timedelta(minutes=30),
                engineer_id=eng_id
            ))

            # Completed Job (Recent)
            db.session.add(Job(
                job_number="JOB-2025-003",
                customer_name="Amit Singh",
                phone="9876543212",
                address="Flat 202, Juhu",
                city="Mumbai",
                job_type="Repair",
                plan="Fiber Basic",
                priority="low",
                status="completed",
                scheduled_at=now - timedelta(days=1),
                started_at=now - timedelta(days=1, hours=2),
                completed_at=now - timedelta(days=1, hours=1),
                engineer_id=eng_id
            ))
            db.session.commit()
            
        print("Seeding complete!")
        
        # Seed Finance Data
        from app.models_finance import Vendor, License
        if not Vendor.query.first():
            print("Seeding Vendors & Licenses...")
            # Vendors
            v1 = Vendor(name="Microsoft Corporation", category="software", monthly_cost=24000, status="active", payment_terms="net30")
            v2 = Vendor(name="Bharti Airtel", category="telecom", monthly_cost=45000, status="active", payment_terms="net15")
            v3 = Vendor(name="SolarWinds", category="software", monthly_cost=15000, status="active", payment_terms="net30")
            
            db.session.add_all([v1, v2, v3])
            db.session.commit()
            
            # Licenses
            from datetime import timedelta, date
            today = date.today()
            
            l1 = License(
                name="Office 365 Business",
                category="software",
                license_number="MS-365-2024",
                vendor_id=v1.id,
                issue_date=today - timedelta(days=300),
                expiry_date=today + timedelta(days=65),
                annual_cost=240000,
                status="active"
            )
            
            l2 = License(
                name="ISP License (Class B)",
                category="regulatory",
                license_number="ISP-MH-2023",
                vendor_id=1, # Hacky but safe for demo if v1 is id 1 or random valid int
                issue_date=today - timedelta(days=700),
                expiry_date=today + timedelta(days=20), # Expiring soon
                annual_cost=500000,
                status="active"
            )
            # Re-fetch v2 to be safe for ID
            l2.vendor_id = v2.id # Assign correct foreign key
            
            l3 = License(
                name="Network Monitoring",
                category="software",
                license_number="NMT-2024",
                vendor_id=v3.id,
                issue_date=today - timedelta(days=100),
                expiry_date=today + timedelta(days=265),
                annual_cost=180000,
                status="active"
            )
            
            db.session.add_all([l1, l2, l3])
            db.session.commit()
            print("Finance data seeded!")

        # Seed Inventory Data
        from app.models_inventory import InventoryItem, StockRequest, StockTransaction
        print("Checking Inventory table...")
        if not InventoryItem.query.first():
            print("Seeding Inventory...")
            i1 = InventoryItem(sku="ONT-5000", name="ONT Model 5000", category="ont", quantity=245, unit_price=2500, min_stock_level=20)
            i2 = InventoryItem(sku="RT-AC5000", name="Router RT-AC5000", category="router", quantity=15, unit_price=1800, min_stock_level=25) # Low stock
            i3 = InventoryItem(sku="FC-100M", name="Fiber Cable 100m", category="cable", quantity=312, unit_price=3500, min_stock_level=30)
            i4 = InventoryItem(sku="SW-8P", name="Switch 8-Port", category="tools", quantity=89, unit_price=1200, min_stock_level=10)
            
            db.session.add_all([i1, i2, i3, i4])
            db.session.commit()
            
            # Vendors
            from app.models_inventory import Vendor as InvVendor
            v1 = InvVendor(name="TechSupply Co.", contact_person="Rajesh Supply", email="sales@techsupply.com", phone="9988776655", category="Hardware")
            v2 = InvVendor(name="FiberNet Supplies", contact_person="Amit Fiber", email="amit@fibernet.com", phone="9988776644", category="Cables")
            db.session.add_all([v1, v2])
            db.session.commit()

            # Requests
            r1 = StockRequest(request_number="REQ-001", engineer_name="Field Engineer", job_id="JOB-8905", items_requested='[{"name": "ONT Model 5000", "qty": 2}, {"name": "Router RT-AC5000", "qty": 2}]', priority="urgent", status="pending")
            r2 = StockRequest(request_number="REQ-002", engineer_name="Field Engineer", job_id="JOB-8906", items_requested='[{"name": "Fiber Cable 100m", "qty": 1}]', priority="normal", status="pending")
            
            db.session.add_all([r1, r2])
            db.session.commit()
            
            # Transactions
            t1 = StockTransaction(item_id=i1.id, transaction_type='IN', quantity=50, reference='INV-2024-0156', performed_by='1', notes='Stock Received')
            t2 = StockTransaction(item_id=i2.id, transaction_type='OUT', quantity=5, reference='J-2024-0089', performed_by='1', notes='Issued to Engineer', created_at=datetime.utcnow() - timedelta(hours=3))
            
            db.session.add_all([t1, t2])
            db.session.commit()
            print("Inventory seeded!")

        # Seed Network Data
        from app.models_network import NetworkDevice, IPPool, IPAllocation, NetworkIncident
        print("Checking Network table...")
        if not NetworkDevice.query.first():
            print("Seeding Network...")
            
            # OLTs
            # Create 48 OLTs as per dashboard requirement
            olts = []
            for i in range(1, 49):
                status = 'online'
                if i in [12, 45, 48]: status = 'offline' # Few offline
                
                olts.append(NetworkDevice(
                    name=f"OLT-{i}",
                    ip_address=f"10.10.1.{i}",
                    device_type='olt',
                    location=f"Location-{i}",
                    status=status,
                    uptime_days=30 if status=='online' else 0,
                    total_ports=128,
                    active_ports=90 if status=='online' else 0
                ))
            db.session.add_all(olts)
            
            # Pools
            p1 = IPPool(name="Public-Pool-1", cidr="103.45.120.0/24", type="public", total_ips=256, used_ips=189)
            p2 = IPPool(name="Private-Pool-Corporate", cidr="10.10.0.0/16", type="private", total_ips=65536, used_ips=2456)
            db.session.add_all([p1, p2])
            db.session.commit()
            
            # Allocations
            a1 = IPAllocation(pool_id=p1.id, ip_address="103.45.120.15", customer_name="Rajesh Kumar", status="active")
            a2 = IPAllocation(pool_id=p1.id, ip_address="103.45.120.16", customer_name="Priya Sharma", status="active")
            db.session.add_all([a1, a2])
            
            # Incidents
            inc1 = NetworkIncident(incident_number="INC-2025-015", title="OLT-12 Power Failure", severity="critical", device_name="OLT-12", description="Complete outage", status="active", affected_count=156, started_at=datetime.now())
            inc2 = NetworkIncident(incident_number="INC-2025-014", title="OLT-45 Signal Degradation", severity="major", device_name="OLT-45", description="High packet loss", status="active", affected_count=12, started_at=datetime.now())
            db.session.add_all([inc1, inc2])
            
            db.session.commit()
            print("Network seeded!")

        # Seed Customer Data
        from app.models import Customer
        if not Customer.query.first():
            print("Seeding Customers...")
            customers = [
                Customer(customer_id="CUS-2025-00001", name="Rahul Dravid", email="rahul@example.com", phone="9876543210", address="Indiranagar, Bangalore", status='active'),
                Customer(customer_id="CUS-2025-00002", name="Sourav Ganguly", email="sourav@example.com", phone="9876543211", address="Kolkata West", status='active')
            ]
            db.session.add_all(customers)
            db.session.commit()
            print("Customers seeded!")

if __name__ == '__main__':
    seed_users()
