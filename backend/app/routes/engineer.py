from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User
from ..models_job import Job
from datetime import datetime, timedelta

bp = Blueprint('engineer', __name__)

@bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    # Filter by user (engineer)
    current_user_id = get_jwt_identity()
    
    status = request.args.get('status')
    
    query = Job.query.filter_by(engineer_id=current_user_id)
    if status and status != 'all':
        query = query.filter_by(status=status)
        
    jobs = query.order_by(Job.scheduled_at.asc()).all()
    return jsonify([j.to_dict() for j in jobs])

@bp.route('/jobs/<int:id>', methods=['GET'])
@jwt_required()
def get_job(id):
    current_user_id = get_jwt_identity()
    # Ensure engineer can only view their own jobs
    job = Job.query.filter_by(id=id, engineer_id=current_user_id).first_or_404()
    return jsonify(job.to_dict())

@bp.route('/jobs/<int:id>/start', methods=['POST'])
@jwt_required()
def start_job(id):
    current_user_id = get_jwt_identity()
    job = Job.query.filter_by(id=id, engineer_id=current_user_id).first_or_404()
    job.status = 'in_progress'
    job.started_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Job started'})

@bp.route('/jobs/<int:id>/complete', methods=['POST'])
@jwt_required()
def complete_job(id):
    current_user_id = get_jwt_identity()
    job = Job.query.filter_by(id=id, engineer_id=current_user_id).first_or_404()
    data = request.json or {}
    
    job.status = 'completed'
    job.completed_at = datetime.utcnow()
    
    if 'devices' in data:
        job.devices = data['devices']
    if 'notes' in data:
        job.notes = data['notes']
        
    db.session.commit()
    return jsonify({'success': True, 'message': 'Job completed'})

@bp.route('/stock-requests', methods=['GET'])
@jwt_required()
def get_stock_requests():
    from ..models_inventory import StockRequest
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    requests = StockRequest.query.filter_by(engineer_name=user.name).order_by(StockRequest.created_at.desc()).all()
    return jsonify([r.to_dict() for r in requests])

@bp.route('/stock-requests', methods=['POST'])
@jwt_required()
def create_stock_request():
    from ..models_inventory import StockRequest
    import json
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    data = request.json
    
    count = StockRequest.query.count() + 1
    req_num = f"REQ-{datetime.utcnow().year}-{count:04d}"
    
    new_req = StockRequest(
        request_number=req_num,
        engineer_name=user.name,
        # job_id could be added if linked to specific job
        items_requested=json.dumps(data.get('items', [])),
        priority=data.get('priority', 'normal'),
        status='pending'
    )
    
    db.session.add(new_req)
    db.session.commit()
    return jsonify(new_req.to_dict()), 201

# --- Service Tickets (Maintenance) ---
@bp.route('/service-tickets', methods=['GET'])
@jwt_required()
def get_service_tickets():
    from ..models_service import ServiceTicket
    current_user_id = get_jwt_identity()
    tickets = ServiceTicket.query.filter_by(created_by_id=current_user_id).order_by(ServiceTicket.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tickets])

@bp.route('/service-tickets', methods=['POST'])
@jwt_required()
def create_service_ticket():
    from ..models_service import ServiceTicket
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    data = request.json
    
    count = ServiceTicket.query.count() + 1
    ticket_num = f"TKT-{datetime.utcnow().year}-{count:04d}"
    
    new_ticket = ServiceTicket(
        ticket_number=ticket_num,
        title=data.get('title'),
        description=data.get('description'),
        priority=data.get('priority', 'medium'),
        category=data.get('category', 'other'),
        created_by_id=current_user_id,
        engineer_name=user.name,
        status='open'
    )
    
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify(new_ticket.to_dict()), 201

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    from ..models_inventory import StockRequest
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Jobs
    jobs_today = Job.query.filter_by(engineer_id=current_user_id).filter(Job.scheduled_at >= today).count()
    in_progress = Job.query.filter_by(engineer_id=current_user_id, status='in_progress').count()
    completed_week = Job.query.filter_by(engineer_id=current_user_id, status='completed').filter(Job.completed_at >= today - timedelta(days=7)).count()
    
    # Materials
    pending_materials = StockRequest.query.filter_by(engineer_name=user.name, status='pending').count()
    
    # Device Distribution (Dynamic)
    completed_jobs = Job.query.filter_by(engineer_id=current_user_id, status='completed').all()
    device_counts = {}
    for j in completed_jobs:
        for d in j.devices:
            d_type = d.get('type', 'other').upper()
            device_counts[d_type] = device_counts.get(d_type, 0) + 1
    
    labels = list(device_counts.keys())
    data = list(device_counts.values())

    if not labels:
        labels = ['ONT', 'Router', 'Cable', 'Connectors']
        data = [0, 0, 0, 0]

    return jsonify({
        'jobs_today': jobs_today,
        'in_progress': in_progress,
        'completed_week': completed_week,
        'pending_materials': pending_materials,
        'travel_time': '24m', # Calculated or placeholder
        'rating': 4.8,       # Calculated or placeholder
        'chart_data': {
            'labels': labels,
            'data': data
        }
    })
