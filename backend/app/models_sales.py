from app import db
from datetime import datetime

class BroadbandPlan(db.Model):
    __tablename__ = 'broadband_plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    speed_mbps = db.Column(db.Integer, nullable=False)
    price_monthly = db.Column(db.Float, nullable=False)
    data_limit_gb = db.Column(db.Integer, default=0) # 0 for unlimited
    validity_days = db.Column(db.Integer, default=30)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'speed_mbps': self.speed_mbps,
            'price_monthly': self.price_monthly,
            'data_limit': 'Unlimited' if self.data_limit_gb == 0 else f"{self.data_limit_gb} GB",
            'validity_days': self.validity_days,
            'description': self.description,
            'is_active': self.is_active
        }
