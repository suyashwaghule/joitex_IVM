from flask import Blueprint, jsonify, request
from app import db
from app.models_finance import Vendor, License
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta

finance_bp = Blueprint('finance', __name__)

# --- Stats ---
@finance_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    # Licenses stats
    total_licenses = License.query.count()
    active_licenses = License.query.filter_by(status='active').count()
    expired_licenses = License.query.filter_by(status='expired').count()
    
    # Expiring soon logic (next 30 days)
    today = datetime.utcnow().date()
    thirty_days_later = today + timedelta(days=30)
    expiring_soon = License.query.filter(
        License.expiry_date >= today,
        License.expiry_date <= thirty_days_later
    ).count()

    # Financials
    total_vendors = Vendor.query.count()
    monthly_spend = db.session.query(db.func.sum(Vendor.monthly_cost)).scalar() or 0
    annual_spend = db.session.query(db.func.sum(License.annual_cost)).scalar() or 0

    # Spend Trend (Mocked)
    spend_chart = {
        'labels': ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'data': [145000, 152000, 148000, 155000, 162000, monthly_spend]
    }

    # Category Spend (Group by category)
    categories = db.session.query(Vendor.category, db.func.sum(Vendor.monthly_cost)).group_by(Vendor.category).all()
    category_chart = {
        'labels': [c[0] for c in categories] if categories else ['No Data'],
        'data': [float(c[1]) for c in categories] if categories else [0]
    }

    return jsonify({
        'licenses': {
            'total': total_licenses,
            'active': active_licenses,
            'expired': expired_licenses,
            'expiring_soon': expiring_soon
        },
        'financials': {
            'total_vendors': total_vendors,
            'monthly_spend': monthly_spend,
            'annual_spend': annual_spend
        },
        'spend_chart': spend_chart,
        'category_chart': category_chart
    })

# --- Vendors ---
@finance_bp.route('/vendors', methods=['GET'])
@jwt_required()
def get_vendors():
    category = request.args.get('category')
    status = request.args.get('status')
    
    query = Vendor.query
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
        
    vendors = query.all()
    return jsonify([v.to_dict() for v in vendors])

@finance_bp.route('/vendors', methods=['POST'])
@jwt_required()
def create_vendor():
    data = request.json
    new_vendor = Vendor(
        name=data['name'],
        category=data['category'],
        contact_person=data.get('contact_person'),
        phone=data.get('phone'),
        email=data.get('email'),
        payment_terms=data.get('payment_terms'),
        address=data.get('address'),
        gst_number=data.get('gst_number'),
        pan_number=data.get('pan_number'),
        monthly_cost=data.get('monthly_cost', 0.0),
        status='active'
    )
    db.session.add(new_vendor)
    db.session.commit()
    return jsonify(new_vendor.to_dict()), 201

# --- Licenses ---
@finance_bp.route('/licenses', methods=['GET'])
@jwt_required()
def get_licenses():
    category = request.args.get('category')
    status = request.args.get('status')
    
    query = License.query
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
        
    licenses = query.all()
    return jsonify([l.to_dict() for l in licenses])

@finance_bp.route('/licenses', methods=['POST'])
@jwt_required()
def create_license():
    data = request.json
    
    # Simple validation manually for now
    try:
        issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d').date()
        expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    new_license = License(
        name=data['name'],
        category=data['category'],
        license_number=data['license_number'],
        vendor_id=data['vendor_id'],
        issue_date=issue_date,
        expiry_date=expiry_date,
        annual_cost=data.get('annual_cost', 0.0),
        status='active',
        notes=data.get('notes')
    )
    db.session.add(new_license)
    db.session.commit()
    return jsonify(new_license.to_dict()), 201
