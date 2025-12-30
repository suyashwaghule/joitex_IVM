from datetime import datetime
from . import db

class Inquiry(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    inquiry_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    service_type = db.Column(db.String(20), nullable=False) # home, business
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending') # pending, forwarded, in_progress, closed, draft
    is_urgent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'inquiry_number': self.inquiry_number,
            'customer_name': self.customer_name,
            'phone': self.phone,
            'email': self.email,
            'service_type': self.service_type,
            'address': self.address,
            'city': self.city,
            'pincode': self.pincode,
            'notes': self.notes,
            'status': self.status,
            'is_urgent': self.is_urgent,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
