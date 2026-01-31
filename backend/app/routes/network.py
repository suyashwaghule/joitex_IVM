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

from app.models_network import NetworkDevice, IPPool, IPAllocation, NetworkIncident, DeviceLog

# ... (Stats endpoint)

# --- OLTs ---
@network_bp.route('/olts', methods=['GET'])
@jwt_required()
def get_olts():
    olts = NetworkDevice.query.filter_by(device_type='olt').all()
    return jsonify([o.to_dict() for o in olts])

from sqlalchemy.exc import IntegrityError

@network_bp.route('/olts', methods=['POST'])
@jwt_required()
def create_olt():
    data = request.json
    
    # Check if IP already exists
    if NetworkDevice.query.filter_by(ip_address=data.get('ip_address')).first():
         return jsonify({'error': 'OLT with this IP address already exists'}), 400

    olt = NetworkDevice(
        name=data.get('name'),
        ip_address=data.get('ip_address'),
        location=data.get('location'),
        device_type='olt',
        total_ports=data.get('total_ports', 8),
        active_ports=0,
        status='online'
    )
    db.session.add(olt)
    
    try:
        db.session.flush() # flush to get ID
        # Auto log
        log = DeviceLog(device_id=olt.id, log_type='system', message='OLT created and initialized.')
        db.session.add(log)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'OLT with this IP address already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    return jsonify(olt.to_dict()), 201

@network_bp.route('/olts/<int:id>', methods=['GET'])
@jwt_required()
def get_olt(id):
    olt = NetworkDevice.query.get_or_404(id)
    return jsonify(olt.to_dict())

@network_bp.route('/olts/<int:id>', methods=['PUT'])
@jwt_required()
def update_olt(id):
    olt = NetworkDevice.query.get_or_404(id)
    data = request.json
    
    updates = []
    if 'name' in data and data['name'] != olt.name:
        updates.append(f"Name changed from '{olt.name}' to '{data['name']}'")
        olt.name = data['name']
    if 'ip_address' in data and data['ip_address'] != olt.ip_address:
        updates.append(f"IP changed from '{olt.ip_address}' to '{data['ip_address']}'")
        olt.ip_address = data['ip_address']
    if 'location' in data and data['location'] != olt.location:
        updates.append(f"Location moved from '{olt.location}' to '{data['location']}'")
        olt.location = data['location']
    if 'total_ports' in data and int(data['total_ports']) != olt.total_ports:
        updates.append(f"Port capacity changed from {olt.total_ports} to {data['total_ports']}")
        olt.total_ports = int(data['total_ports'])
    
    if updates:
        for msg in updates:
            log = DeviceLog(device_id=olt.id, log_type='info', message=msg)
            db.session.add(log)
        db.session.commit()
        
    return jsonify(olt.to_dict())

@network_bp.route('/olts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_olt(id):
    olt = NetworkDevice.query.get_or_404(id)
    db.session.delete(olt)
    db.session.commit()
    return jsonify({'message': 'OLT deleted'})

@network_bp.route('/olts/<int:id>/logs', methods=['GET'])
@jwt_required()
def get_olt_logs(id):
    olt = NetworkDevice.query.get_or_404(id) # check exists
    logs = DeviceLog.query.filter_by(device_id=id).order_by(DeviceLog.created_at.desc()).limit(100).all()
    return jsonify([l.to_dict() for l in logs])

# --- IPAM ---
@network_bp.route('/ipam/pools', methods=['GET'])
@jwt_required()
def get_pools():
    pools = IPPool.query.all()
    return jsonify([p.to_dict() for p in pools])

@network_bp.route('/ipam/pools/<int:id>', methods=['GET'])
@jwt_required()
def get_pool(id):
    pool = IPPool.query.get_or_404(id)
    return jsonify(pool.to_dict())

@network_bp.route('/ipam/allocations', methods=['GET'])
@jwt_required()
def get_allocations():
    allocations = IPAllocation.query.order_by(IPAllocation.assigned_at.desc()).limit(50).all()
    return jsonify([a.to_dict() for a in allocations])

@network_bp.route('/ipam/allocations', methods=['POST'])
@jwt_required()
def allocate_ip():
    import ipaddress
    import random
    
    data = request.json
    pool_id = data.get('pool_id')
    
    pool = IPPool.query.get(pool_id)
    if not pool:
        return jsonify({'error': 'Pool not found'}), 404
        
    if pool.used_ips >= pool.total_ips:
        return jsonify({'error': 'Pool exhausted'}), 400
        
    requested_ip = data.get('ip_address')
    
    # Auto-allocate logic
    if not requested_ip:
        try:
            network = ipaddress.ip_network(pool.cidr, strict=False)
            # Get all allocated IPs for this pool
            existing = set(a.ip_address for a in IPAllocation.query.filter_by(pool_id=pool.id).all())
            
            # Simple random fetch strategy for demo (efficient enough for small pools)
            # Avoid network and broadcast address
            available_hosts = list(network.hosts())
            if not available_hosts:
                 return jsonify({'error': 'No hosts available in subnet'}), 400
                 
            # filter out used
            candidates = [str(ip) for ip in available_hosts if str(ip) not in existing]
            
            if not candidates:
                 return jsonify({'error': 'Pool visually exhausted (fragmentation)'}), 400
                 
            requested_ip = random.choice(candidates)
            
        except ValueError:
            # Fallback if CIDR is invalid
            requested_ip = f"103.45.120.{random.randint(2, 254)}"

    # Create allocation
    new_alloc = IPAllocation(
        pool_id=pool.id,
        ip_address=requested_ip,
        customer_name=data.get('customer_name', 'Unknown User'),
        mac_address=data.get('mac_address', ''),
        status='active'
    )
    
    pool.used_ips += 1
    db.session.add(new_alloc)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Allocation failed', 'details': str(e)}), 400
    
    return jsonify(new_alloc.to_dict()), 201

@network_bp.route('/ipam/pools', methods=['POST'])
@jwt_required()
def create_pool():
    data = request.json
    try:
        pool = IPPool(
            name=data.get('name'),
            cidr=data.get('cidr'),
            gateway=data.get('gateway'),
            type=data.get('pool_type', 'public'), # Frontend sends pool_type
            total_ips=data.get('total_ips', 256),
            used_ips=0,
            description=data.get('description', '')
        )
        db.session.add(pool)
        db.session.commit()
        return jsonify(pool.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@network_bp.route('/ipam/pools/<int:id>', methods=['PUT'])
@jwt_required()
def update_pool(id):
    pool = IPPool.query.get_or_404(id)
    data = request.json
    if 'name' in data: pool.name = data['name']
    if 'gateway' in data: pool.gateway = data['gateway']
    if 'description' in data: pool.description = data['description']
    if 'pool_type' in data: pool.type = data['pool_type']
    db.session.commit()
    return jsonify(pool.to_dict())

@network_bp.route('/ipam/pools/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_pool(id):
    pool = IPPool.query.get_or_404(id)
    db.session.delete(pool)
    db.session.commit()
    return jsonify({'message': 'Pool deleted'})

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
