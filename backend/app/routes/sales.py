from flask import Blueprint, jsonify, request
from app import db
from app.models import Lead, User
from app.models_sales import BroadbandPlan
from app.models_inquiry import Inquiry
from app.models_job import Job
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta

sales_bp = Blueprint('sales', __name__)

# --- Stats ---
@sales_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    # New From Call Center (Inquiries forwarded to sales/leads not yet processed)
    # Assuming 'forwarded' inquiries are new leads
    new_inquiries = Inquiry.query.filter_by(status='forwarded').count()
    
    # Feasibility Pending
    feasibility_pending = Lead.query.filter_by(status='feasibility').count()
    
    # In Progress (Jobs)
    installations_progress = Job.query.filter_by(status='in_progress', job_type='New Installation').count()
    
    # Leads Closed (Installed Leads this month)
    today = datetime.utcnow()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    leads_closed = Lead.query.filter(Lead.status == 'installed', Lead.updated_at >= month_start).count()
    
    # Pipeline Data (Mocked for speed if complex queries needed)
    # Pipeline Data
    pipeline_data = {
        'labels': ['New', 'Feasibility', 'In Progress', 'Installed', 'Cancelled'],
        'data': [
            Lead.query.filter_by(status='new').count(),
            Lead.query.filter_by(status='feasibility').count(),
            Lead.query.filter_by(status='in_progress').count(),
            leads_closed,
            Lead.query.filter_by(status='cancelled').count()
        ]
    }

    # Conversion Data
    total_leads = Lead.query.count()
    converted = Lead.query.filter_by(status='installed').count()
    cancelled = Lead.query.filter_by(status='cancelled').count()
    in_progress = total_leads - converted - cancelled
    
    conversion_data = {
        'labels': ['Converted', 'In Progress', 'Lost'],
        'data': [converted, in_progress, cancelled]
    }

    return jsonify({
        'kpi': {
            'new_inquiries': new_inquiries,
            'feasibility_pending': feasibility_pending,
            'installations_progress': installations_progress,
            'leads_closed': leads_closed
        },
        'pipeline_chart': pipeline_data,
        'conversion': conversion_data
    })

# --- Leads ---
@sales_bp.route('/leads', methods=['GET'])
@jwt_required()
def get_leads():
    status = request.args.get('status')
    query = Lead.query
    if status:
        query = query.filter_by(status=status)
    
    leads = query.order_by(Lead.created_at.desc()).limit(50).all()
    return jsonify([l.to_dict() for l in leads])

@sales_bp.route('/leads', methods=['POST'])
@jwt_required()
def create_lead():
    data = request.json
    count = Lead.query.count() + 1
    new_lead = Lead(
        lead_number=f"L-2025-{count:04d}",
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        plan_interest=data.get('plan_interest'),
        status='new',
        source='manual'
    )
    db.session.add(new_lead)
    db.session.commit()
    return jsonify(new_lead.to_dict()), 201

@sales_bp.route('/leads/<int:id>/status', methods=['POST'])
@jwt_required()
def update_lead_status(id):
    lead = Lead.query.get_or_404(id)
    data = request.json
    new_status = data.get('status')
    
    if new_status:
        lead.status = new_status
        # logic to create Job if status becomes 'installed' or 'in_progress' could go here
        
    db.session.commit()
    return jsonify(lead.to_dict())

# --- Plans ---
@sales_bp.route('/plans', methods=['GET'])
@jwt_required()
def get_plans():
    plans = BroadbandPlan.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in plans])

# --- Feasibility Queue ---
@sales_bp.route('/feasibility', methods=['GET'])
@jwt_required()
def get_feasibility_queue():
    # Return leads marked for feasibility check
    leads = Lead.query.filter_by(status='feasibility').all()
    # Or queries marked as 'forwarded' that need feasibility
    q_inq = Inquiry.query.filter_by(status='forwarded').limit(10).all()
    
    results = []
    # Merge for display
    for i in q_inq:
        results.append({
            'type': 'inquiry',
            'id': i.inquiry_number,
            'name': i.customer_name,
            'address': i.address,
            'priority': 'high' if i.is_urgent else 'normal'
        })
    for l in leads:
        results.append({
            'type': 'lead',
            'id': l.lead_number,
            'name': l.name,
            'address': l.address,
            'priority': 'normal'
        })
        
    return jsonify(results)

@sales_bp.route('/assignments', methods=['GET'])
@jwt_required()
def get_assignments():
    # Return scheduled jobs
    jobs = Job.query.filter(Job.status.in_(['pending', 'in_progress'])).order_by(Job.scheduled_at).limit(5).all()
    return jsonify([j.to_dict() for j in jobs])

@sales_bp.route('/feasibility/<string:id>/approve', methods=['POST'])
@jwt_required()
def approve_feasibility(id):
    # 'id' can be inquiry_number or lead_number
    if id.startswith('INQ'):
        item = Inquiry.query.filter_by(inquiry_number=id).first_or_404()
        item.status = 'in_progress'
        # Create a Lead from this inquiry
        count = Lead.query.count() + 1
        new_lead = Lead(
            lead_number=f"L-2025-{count:04d}",
            name=item.customer_name,
            email=item.email,
            phone=item.phone,
            address=item.address,
            status='feasibility',
            source='call_center'
        )
        db.session.add(new_lead)
    elif id.startswith('L-'):
        item = Lead.query.filter_by(lead_number=id).first_or_404()
        item.status = 'feasibility_passed' # Ready for quote/installation schedule
    
    db.session.commit()
    return jsonify({'message': 'Feasibility approved'})

@sales_bp.route('/feasibility/<string:id>/reject', methods=['POST'])
@jwt_required()
def reject_feasibility(id):
    if id.startswith('INQ'):
        item = Inquiry.query.filter_by(inquiry_number=id).first_or_404()
        item.status = 'closed'
    elif id.startswith('L-'):
        item = Lead.query.filter_by(lead_number=id).first_or_404()
        item.status = 'cancelled'
    
    db.session.commit()
    return jsonify({'message': 'Feasibility rejected'})

@sales_bp.route('/installations/schedule', methods=['POST'])
@jwt_required()
def schedule_installation():
    data = request.json
    lead_id = data.get('lead_id')
    lead = Lead.query.filter_by(lead_number=lead_id).first_or_404()
    
    count = Job.query.count() + 1
    new_job = Job(
        job_number=f"JOB-2025-{count:04d}",
        customer_name=lead.name,
        phone=lead.phone,
        address=lead.address,
        job_type='New Installation',
        plan=lead.plan_interest,
        priority='medium',
        status='pending',
        scheduled_at=datetime.fromisoformat(data.get('scheduled_at')),
        engineer_id=data.get('engineer_id') if data.get('engineer_id') else 1,
        lead_id=lead.id
    )
    
    lead.status = 'in_progress'
    db.session.add(new_job)
    db.session.commit()
    return jsonify(new_job.to_dict()), 201

@sales_bp.route('/activations', methods=['GET'])
@jwt_required()
def get_activation_queue():
    # Return jobs that are completed but not necessarily activated
    jobs = Job.query.filter_by(status='completed').all()
    return jsonify([j.to_dict() for j in jobs])

@sales_bp.route('/activations/<string:job_number>/activate', methods=['POST'])
@jwt_required()
def activate_service(job_number):
    from app.models import Customer
    job = Job.query.filter_by(job_number=job_number).first_or_404()
    
    # Create Customer
    count = Customer.query.count() + 1
    new_cust = Customer(
        customer_id=f"CUS-2025-{count:05d}",
        name=job.customer_name,
        phone=job.phone,
        address=job.address,
        status='active'
    )
    
    # Update lead status to installed
    if job.lead_id:
        lead = Lead.query.get(job.lead_id)
        if lead:
            lead.status = 'installed'
    
    db.session.add(new_cust)
    db.session.commit()
    return jsonify(new_cust.to_dict())

@sales_bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    from app.models import Customer
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers])

@sales_bp.route('/engineers', methods=['GET'])
@jwt_required()
def get_engineers():
    engineers = User.query.filter_by(role='engineer').all()
    return jsonify([{'id': u.id, 'name': u.name} for u in engineers])
