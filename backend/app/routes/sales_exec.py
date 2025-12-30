from flask import Blueprint, jsonify, request
from app import db
from app.models import Lead, User
from app.models_sales import BroadbandPlan
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

sales_exec_bp = Blueprint('sales_exec', __name__)

# --- Stats ---
@sales_exec_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    current_user_id = get_jwt_identity()
    
    # My Leads (Open)
    # Open leads are those not converted (installed) or cancelled
    my_leads_open = Lead.query.filter(
        Lead.assigned_to == current_user_id,
        Lead.status.notin_(['installed', 'cancelled'])
    ).count()
    
    # Follow-ups Today (Real logic: leads with follow_up_date today or earlier and not installed/cancelled)
    now = datetime.utcnow()
    today_end = now.replace(hour=23, minute=59, second=59)
    follow_ups = Lead.query.filter(
        Lead.assigned_to == current_user_id,
        Lead.status.notin_(['installed', 'cancelled']),
        Lead.follow_up_date <= today_end
    ).count()
    
    # Converted (MTD)
    today = datetime.utcnow()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    converted_mtd = Lead.query.filter(
        Lead.assigned_to == current_user_id,
        Lead.status == 'installed',
        Lead.updated_at >= month_start
    ).count()
    
    # Conversion Rate (Mocked calculation)
    total_leads = Lead.query.filter_by(assigned_to=current_user_id).count()
    total_converted = Lead.query.filter_by(assigned_to=current_user_id, status='installed').count()
    conversion_rate = round((total_converted / total_leads * 100) if total_leads > 0 else 0, 1)

    # Pipeline Chart (Last 4 weeks)
    labels = []
    new_data = []
    conv_data = []
    for i in range(3, -1, -1):
        start = now - timedelta(days=(i+1)*7)
        end = now - timedelta(days=i*7)
        labels.append(f"Week {4-i}")
        
        n_count = Lead.query.filter(
            Lead.assigned_to == current_user_id,
            Lead.created_at >= start,
            Lead.created_at <= end
        ).count()
        
        c_count = Lead.query.filter(
            Lead.assigned_to == current_user_id,
            Lead.status == 'installed',
            Lead.updated_at >= start,
            Lead.updated_at <= end
        ).count()
        
        new_data.append(n_count)
        conv_data.append(c_count)

    return jsonify({
        'kpi': {
            'my_leads_open': my_leads_open,
            'follow_ups': follow_ups,
            'converted_mtd': converted_mtd,
            'conversion_rate': conversion_rate
        },
        'pipeline_chart': {
            'labels': labels,
            'datasets': [
                {'label': 'New Leads', 'data': new_data, 'backgroundColor': 'rgba(99, 102, 241, 0.8)'},
                {'label': 'Converted', 'data': conv_data, 'backgroundColor': 'rgba(34, 197, 94, 0.8)'}
            ]
        }
    })

# --- Leads ---
@sales_exec_bp.route('/leads', methods=['GET'])
@jwt_required()
def get_leads():
    current_user_id = get_jwt_identity()
    status = request.args.get('status')
    
    query = Lead.query.filter_by(assigned_to=current_user_id)
    if status:
        # Map frontend badgestatus to backend status if needed, or assume consistent
        if status == 'open':
            query = query.filter(Lead.status.notin_(['installed', 'cancelled']))
        elif status == 'converted':
            query = query.filter_by(status='installed')
        else:
            query = query.filter_by(status=status)
            
    leads = query.order_by(Lead.created_at.desc()).limit(50).all()
    return jsonify([l.to_dict() for l in leads])

@sales_exec_bp.route('/leads', methods=['POST'])
@jwt_required()
def create_lead():
    current_user_id = get_jwt_identity()
    data = request.json
    
    # Generate Lead Number
    # In production, use a more robust sequence or UUID
    count = Lead.query.count() + 1
    lead_number = f"L-2025-{count:04d}"
    
    new_lead = Lead(
        lead_number=lead_number,
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        plan_interest=data.get('plan_interest'),
        status='new',
        source=data.get('source', 'sales_exec'),
        assigned_to=current_user_id,
        follow_up_date=datetime.fromisoformat(data['follow_up_date']) if data.get('follow_up_date') else None,
        notes=data.get('notes')
    )
    
    db.session.add(new_lead)
    db.session.commit()
    
    return jsonify(new_lead.to_dict()), 201

@sales_exec_bp.route('/leads/<string:id>', methods=['GET'])
@jwt_required()
def get_lead(id):
    current_user_id = get_jwt_identity()
    lead = Lead.query.filter_by(lead_number=id, assigned_to=current_user_id).first_or_404()
    return jsonify(lead.to_dict())

@sales_exec_bp.route('/leads/<string:id>', methods=['PUT'])
@jwt_required()
def update_lead(id):
    current_user_id = get_jwt_identity()
    lead = Lead.query.filter_by(lead_number=id, assigned_to=current_user_id).first_or_404()
    data = request.json
    
    if 'status' in data:
        lead.status = data['status']
    if 'plan_interest' in data:
        lead.plan_interest = data['plan_interest']
    if 'address' in data:
        lead.address = data['address']
    if 'follow_up_date' in data:
        lead.follow_up_date = datetime.fromisoformat(data['follow_up_date']) if data['follow_up_date'] else None
    if 'notes' in data:
        lead.notes = data['notes']
        
    db.session.commit()
    return jsonify(lead.to_dict())

@sales_exec_bp.route('/plans', methods=['GET'])
@jwt_required()
def get_plans():
    plans = BroadbandPlan.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in plans])
