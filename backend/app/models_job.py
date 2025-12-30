from datetime import datetime
import json
from . import db

class Job(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    job_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50))
    job_type = db.Column(db.String(50), nullable=False) # New Install, Upgrade, Repair
    plan = db.Column(db.String(100))
    priority = db.Column(db.String(20), default='medium') # high, medium, low
    status = db.Column(db.String(20), default='pending') # pending, in_progress, completed
    scheduled_at = db.Column(db.DateTime, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    devices_json = db.Column(db.Text) # To store installed devices as JSON
    engineer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'))

    @property
    def devices(self):
        return json.loads(self.devices_json) if self.devices_json else []
    
    @devices.setter
    def devices(self, value):
        self.devices_json = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'job_number': self.job_number,
            'customer_name': self.customer_name,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'job_type': self.job_type,
            'plan': self.plan,
            'priority': self.priority,
            'status': self.status,
            'scheduled_at': self.scheduled_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'devices': self.devices,
            'lead_id': self.lead_id
        }
