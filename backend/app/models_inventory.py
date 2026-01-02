from app import db
from datetime import datetime

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    unit_price = db.Column(db.Float, default=0.0)
    quantity = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        status = 'in_stock'
        if self.quantity == 0:
            status = 'out_of_stock'
        elif self.quantity <= self.min_stock_level:
            status = 'low_stock'

        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'unit_price': self.unit_price,
            'quantity': self.quantity,
            'min_stock_level': self.min_stock_level,
            'status': status,
            'created_at': self.created_at.isoformat()
        }

class StockTransaction(db.Model):
    __tablename__ = 'stock_transactions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False) # 'in', 'out', 'return'
    quantity = db.Column(db.Integer, nullable=False)
    reference = db.Column(db.String(100)) # e.g. Invoice #, Job #
    performed_by = db.Column(db.String(100)) # User name or ID
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    item = db.relationship('InventoryItem', backref=db.backref('transactions', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_name': self.item.name if self.item else 'Unknown',
            'transaction_type': self.transaction_type,
            'quantity': self.quantity,
            'reference': self.reference,
            'performed_by': self.performed_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class StockRequest(db.Model):
    __tablename__ = 'stock_requests'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(50), unique=True, nullable=False)
    engineer_name = db.Column(db.String(100), nullable=False)
    job_id = db.Column(db.String(50))
    items_requested = db.Column(db.Text) # JSON string: [{"item_name": "...", "quantity": 1}, ...]
    priority = db.Column(db.String(20), default='normal') # normal, urgent
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        try:
            items = json.loads(self.items_requested)
        except:
            items = []
            
        return {
            'id': self.id,
            'request_number': self.request_number,
            'engineer_name': self.engineer_name,
            'job_id': self.job_id,
            'items_requested': items,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Vendor(db.Model):
    __tablename__ = 'inventory_vendors'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    category = db.Column(db.String(50))
    address = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'category': self.category,
            'address': self.address,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


