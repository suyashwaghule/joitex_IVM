from app import db
from datetime import datetime

class NetworkDevice(db.Model):
    __tablename__ = 'network_devices'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(20), unique=True, nullable=False)
    device_type = db.Column(db.String(50), default='olt') # olt, switch, router
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='online') # online, offline, maintenance
    uptime_days = db.Column(db.Integer, default=0)
    total_ports = db.Column(db.Integer, default=0)
    active_ports = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'device_type': self.device_type,
            'location': self.location,
            'status': self.status,
            'uptime_days': self.uptime_days,
            'total_ports': self.total_ports,
            'active_ports': self.active_ports,
            'utilization': round((self.active_ports / self.total_ports * 100) if self.total_ports > 0 else 0, 1)
        }

class IPPool(db.Model):
    __tablename__ = 'ip_pools'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cidr = db.Column(db.String(50), nullable=False)
    gateway = db.Column(db.String(20))
    type = db.Column(db.String(20), default='public') # public, private, management
    total_ips = db.Column(db.Integer, default=0)
    used_ips = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to individual allocations (if we were storing them individually)
    # For now, we'll store allocations simply or just track counters.
    # Let's add a list of allocations
    allocations = db.relationship('IPAllocation', backref='pool', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cidr': self.cidr,
            'gateway': self.gateway,
            'type': self.type,
            'total_ips': self.total_ips,
            'used_ips': self.used_ips, # Could be calculated from allocations len but storing for fast access is fine 
            'utilization': round((self.used_ips / self.total_ips * 100) if self.total_ips > 0 else 0, 1),
            'description': self.description
        }

class IPAllocation(db.Model):
    __tablename__ = 'ip_allocations'

    id = db.Column(db.Integer, primary_key=True)
    pool_id = db.Column(db.Integer, db.ForeignKey('ip_pools.id'), nullable=False)
    ip_address = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(100)) # Or link to User/Job
    mac_address = db.Column(db.String(50))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active') # active, released

    def to_dict(self):
        return {
            'id': self.id,
            'pool_id': self.pool_id,
            'pool_name': self.pool.name if self.pool else 'Unknown',
            'ip_address': self.ip_address,
            'customer_name': self.customer_name,
            'mac_address': self.mac_address,
            'assigned_at': self.assigned_at.isoformat(),
            'status': self.status
        }

class NetworkIncident(db.Model):
    __tablename__ = 'network_incidents'

    id = db.Column(db.Integer, primary_key=True)
    incident_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.String(20), nullable=False) # critical, major, minor
    device_name = db.Column(db.String(100)) # e.g. OLT name
    description = db.Column(db.Text)
    root_cause = db.Column(db.Text)
    status = db.Column(db.String(20), default='active') # active, investigating, resolved
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    affected_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        duration = None
        if self.resolved_at:
             diff = self.resolved_at - self.started_at
             hours = diff.total_seconds() / 3600
             duration = f"{round(hours, 1)}h"
        
        return {
            'id': self.id,
            'incident_number': self.incident_number,
            'title': self.title,
            'severity': self.severity,
            'device_name': self.device_name,
            'description': self.description,
            'root_cause': self.root_cause,
            'status': self.status,
            'started_at': self.started_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'duration': duration,
            'affected_count': self.affected_count
        }
