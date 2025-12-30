from flask import Blueprint, jsonify, request
from app import db
from app.models_network import NetworkDevice, IPPool, IPAllocation, NetworkIncident
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta

network_bp = Blueprint('network', __name__)

# --- Stats ---
@network_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    # Devices
    olts = NetworkDevice.query.filter_by(device_type='olt').all()
    olt_online = sum(1 for o in olts if o.status == 'online')
    olt_offline = sum(1 for o in olts if o.status == 'offline')
    
    # Incidents
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    alerts_today = NetworkIncident.query.filter(NetworkIncident.started_at >= today_start).count()
    active_incidents = NetworkIncident.query.filter(NetworkIncident.status != 'resolved').count()
    
    # IP Stats
    pools = IPPool.query.all()
    total_ips = sum(p.total_ips for p in pools)
    used_ips = sum(p.used_ips for p in pools)
    
    # Chart: Uptime (Calculated from incidents)
    today = datetime.utcnow().date()
    labels = []
    data = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%a')
        labels.append(day_str)
        
        # Calculate downtime for this day
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        # Find incidents active during this day
        # An incident affects this day if it started before day_end AND (ended after day_start OR is active)
        incidents = NetworkIncident.query.filter(
            NetworkIncident.started_at <= day_end,
            (NetworkIncident.resolved_at >= day_start) | (NetworkIncident.resolved_at == None)
        ).all()
        
        downtime_minutes = 0
        for inc in incidents:
            # Calculate overlap duration
            inc_start = max(inc.started_at, day_start)
            inc_end = min(inc.resolved_at or datetime.utcnow(), day_end)
            if inc_end > inc_start:
                duration = (inc_end - inc_start).total_seconds() / 60
                downtime_minutes += duration
        
        total_minutes = 24 * 60
        uptime_pct = max(0, 100 - (downtime_minutes / total_minutes * 100))
        data.append(round(uptime_pct, 2))

    # Outage Distribution (Last 30 days)
    month_start = today - timedelta(days=30)
    inc_30d = NetworkIncident.query.filter(NetworkIncident.started_at >= month_start).all()
    outage_dist = {
        'labels': ['Critical', 'Major', 'Minor', 'Informational'],
        'data': [
            sum(1 for i in inc_30d if i.severity == 'critical'),
            sum(1 for i in inc_30d if i.severity == 'major'),
            sum(1 for i in inc_30d if i.severity == 'minor'),
            sum(1 for i in inc_30d if i.severity == 'info')
        ]
    }

    uptime_chart = {
        'labels': labels,
        'data': data
    }

    return jsonify({
        'kpi': {
            'olts_online': olt_online,
            'olts_total': len(olts),
            'olts_offline': olt_offline,
            'alerts_today': alerts_today,
            'active_incidents': active_incidents,
            'ip_utilization': round((used_ips / total_ips * 100) if total_ips > 0 else 0, 1),
            'ip_used': used_ips,
            'ip_total': total_ips
        },
        'uptime_chart': uptime_chart,
        'outage_distribution': outage_dist
    })

# --- OLTs ---
@network_bp.route('/olts', methods=['GET'])
@jwt_required()
def get_olts():
    olts = NetworkDevice.query.filter_by(device_type='olt').all()
    return jsonify([o.to_dict() for o in olts])

@network_bp.route('/olts/<int:id>', methods=['GET'])
@jwt_required()
def get_olt(id):
    olt = NetworkDevice.query.get_or_404(id)
    return jsonify(olt.to_dict())

# --- IPAM ---
@network_bp.route('/ipam/pools', methods=['GET'])
@jwt_required()
def get_pools():
    pools = IPPool.query.all()
    return jsonify([p.to_dict() for p in pools])

@network_bp.route('/ipam/allocations', methods=['GET'])
@jwt_required()
def get_allocations():
    allocations = IPAllocation.query.order_by(IPAllocation.assigned_at.desc()).limit(50).all()
    return jsonify([a.to_dict() for a in allocations])

@network_bp.route('/ipam/allocations', methods=['POST'])
@jwt_required()
def allocate_ip():
    data = request.json
    pool_id = data.get('pool_id')
    
    pool = IPPool.query.get(pool_id)
    if not pool:
        return jsonify({'error': 'Pool not found'}), 404
        
    if pool.used_ips >= pool.total_ips:
        return jsonify({'error': 'Pool exhausted'}), 400
        
    # In a real app, logic to find next free IP based on CIDR
    # Here we simulate by just taking inputs or random
    new_alloc = IPAllocation(
        pool_id=pool.id,
        ip_address=data.get('ip_address', '103.45.120.x'), # Should validate or generate
        customer_name=data.get('customer_name'),
        mac_address=data.get('mac_address', ''),
        status='active'
    )
    
    pool.used_ips += 1
    db.session.add(new_alloc)
    db.session.commit()
    
    return jsonify(new_alloc.to_dict()), 201

@network_bp.route('/ipam/pools', methods=['POST'])
@jwt_required()
def create_pool():
    data = request.json
    pool = IPPool(
        name=data.get('name'),
        cidr=data.get('cidr'),
        gateway=data.get('gateway'),
        pool_type=data.get('pool_type', 'public'),
        total_ips=data.get('total_ips', 256),
        used_ips=0,
        description=data.get('description', '')
    )
    db.session.add(pool)
    db.session.commit()
    return jsonify(pool.to_dict()), 201

@network_bp.route('/ipam/allocations/<int:id>', methods=['DELETE'])
@jwt_required()
def release_allocation(id):
    alloc = IPAllocation.query.get_or_404(id)
    pool = IPPool.query.get(alloc.pool_id)
    if pool:
        pool.used_ips = max(0, pool.used_ips - 1)
    
    db.session.delete(alloc)
    db.session.commit()
    return jsonify({'message': 'Allocation released'})

# --- Incidents ---
@network_bp.route('/incidents', methods=['GET'])
@jwt_required()
def get_incidents():
    incidents = NetworkIncident.query.order_by(NetworkIncident.started_at.desc()).all()
    return jsonify([i.to_dict() for i in incidents])

@network_bp.route('/incidents', methods=['POST'])
@jwt_required()
def create_incident():
    data = request.json
    inc = NetworkIncident(
        incident_number=f"INC-{datetime.now().strftime('%Y%m%d%H%M')}",
        title=data.get('title'),
        severity=data.get('severity'),
        device_name=data.get('device_name'),
        description=data.get('description'),
        root_cause=data.get('root_cause'),
        status='active',
        affected_count=data.get('affected_count', 0)
    )
    db.session.add(inc)
    db.session.commit()
    return jsonify(inc.to_dict()), 201

@network_bp.route('/incidents/<int:id>/resolve', methods=['POST'])
@jwt_required()
def resolve_incident(id):
    inc = NetworkIncident.query.get_or_404(id)
    inc.status = 'resolved'
    inc.resolved_at = datetime.utcnow()
    db.session.commit()
    return jsonify(inc.to_dict())
