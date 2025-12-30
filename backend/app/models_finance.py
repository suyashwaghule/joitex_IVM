from app import db
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # software, telecom, infrastructure, equipment
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    payment_terms = db.Column(db.String(50)) # net15, net30, cod, etc.
    address = db.Column(db.Text)
    gst_number = db.Column(db.String(50))
    pan_number = db.Column(db.String(50))
    monthly_cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active') # active, inactive, pending_payment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    licenses = db.relationship('License', backref='vendor', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'payment_terms': self.payment_terms,
            'address': self.address,
            'gst_number': self.gst_number,
            'pan_number': self.pan_number,
            'monthly_cost': self.monthly_cost,
            'status': self.status,
            'license_count': len(self.licenses)
        }

class License(db.Model):
    __tablename__ = 'licenses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # software, regulatory, telecom, infrastructure
    license_number = db.Column(db.String(100), unique=True, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    annual_cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active') # active, expiring, expired
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'license_number': self.license_number,
            'vendor_id': self.vendor_id,
            'vendor_name': self.vendor.name if self.vendor else 'Unknown',
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'annual_cost': self.annual_cost,
            'status': self.status,
            'notes': self.notes
        }
