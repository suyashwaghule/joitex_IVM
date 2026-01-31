from . import db
from datetime import datetime
import json

class User(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100))
    role = db.Column(db.String(50))
    permissions_json = db.Column(db.Text) 
    portals_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_logout = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    @property
    def permissions(self):
        return json.loads(self.permissions_json) if self.permissions_json else []
    
    @permissions.setter
    def permissions(self, value):
        self.permissions_json = json.dumps(value)

    @property
    def portals(self):
        return json.loads(self.portals_json) if self.portals_json else []

    @portals.setter
    def portals(self, value):
        self.portals_json = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'permissions': self.permissions,
            'portals': self.portals,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_logout': self.last_logout.isoformat() if self.last_logout else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    color = db.Column(db.String(20), default='#1976d2')
    permissions_json = db.Column(db.Text)
    is_system = db.Column(db.Boolean, default=False)
    
    @property
    def permissions(self):
        return json.loads(self.permissions_json) if self.permissions_json else []
    
    @permissions.setter
    def permissions(self, value):
        self.permissions_json = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'permissions': self.permissions,
            'is_system': self.is_system
        }

class Lead(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    lead_number = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    plan_interest = db.Column(db.String(100))
    status = db.Column(db.String(50), default='new') # new, feasibility, in_progress, installed, cancelled
    source = db.Column(db.String(50), default='manual') # manual, website, referral
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    follow_up_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'lead_number': self.lead_number,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'plan_interest': self.plan_interest,
            'status': self.status,
            'source': self.source,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Customer(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    plan_id = db.Column(db.Integer, db.ForeignKey('broadband_plans.id'))
    status = db.Column(db.String(20), default='active') # active, suspended, terminated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class OLT(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    status = db.Column(db.String(20)) # online, offline, maintenance
    sectors = db.Column(db.Integer, default=0)
    connected_users = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    stock_level = db.Column(db.Integer, default=0)
    min_threshold = db.Column(db.Integer, default=10)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserLog(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False) # login, logout, update, create, delete
    details = db.Column(db.Text) # JSON string or text description
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat()
        }
