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
    # Filter by engineer name for now as StockRequest uses name string
    requests = StockRequest.query.filter_by(engineer_name=user.name).all()
    return jsonify([r.to_dict() for r in requests])

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
    # Count device types from completed jobs
    completed_jobs = Job.query.filter_by(engineer_id=current_user_id, status='completed').all()
    device_counts = {}
    for j in completed_jobs:
        # job.devices property handles JSON parsing
        for d in j.devices:
            d_type = d.get('type', 'other').upper()
            device_counts[d_type] = device_counts.get(d_type, 0) + 1
    
    labels = list(device_counts.keys())
    data = list(device_counts.values())

    if not labels:
        # Fallback for empty chart
        labels = ['ONT', 'Router', 'Cable', 'Connectors']
        data = [0, 0, 0, 0]

    return jsonify({
        'jobs_today': jobs_today,
        'in_progress': in_progress,
        'completed_week': completed_week,
        'pending_materials': pending_materials,
        'chart_data': {
            'labels': labels,
            'data': data
        }
    })
