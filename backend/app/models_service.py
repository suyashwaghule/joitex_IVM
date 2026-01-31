from app import db
from datetime import datetime

class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium') # low, medium, high
    status = db.Column(db.String(20), default='open') # open, in_progress, resolved, closed
    category = db.Column(db.String(50)) # network, hardware, software, other
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    engineer_name = db.Column(db.String(100)) # Store name for easy display
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_number': self.ticket_number,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'category': self.category,
            'engineer_name': self.engineer_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
