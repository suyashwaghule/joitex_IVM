from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User
from ..models_inquiry import Inquiry
import uuid

bp = Blueprint('callcenter', __name__)

@bp.route('/inquiries', methods=['GET'])
@jwt_required()
def get_inquiries():
    # Filter params
    status = request.args.get('status')
    search = request.args.get('search')
    
    query = Inquiry.query
    
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(Inquiry.customer_name.like(f'%{search}%') | Inquiry.phone.like(f'%{search}%'))
        
    inquiries = query.order_by(Inquiry.created_at.desc()).all()
    return jsonify([i.to_dict() for i in inquiries])

@bp.route('/inquiries', methods=['POST'])
@jwt_required()
def create_inquiry():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # Generate ID
    inquiry_num = f"INQ-{uuid.uuid4().hex[:6].upper()}"
    
    new_inquiry = Inquiry(
        inquiry_number=inquiry_num,
        customer_name=data['customerName'],
        phone=data['phone'],
        email=data.get('email'),
        service_type=data['serviceType'],
        address=data['address'],
        city=data['city'],
        pincode=data['pincode'],
        notes=data.get('notes'),
        status=data.get('action', 'pending') == 'draft' and 'draft' or 'pending',
        is_urgent=data.get('urgent', False),
        created_by_id=user_id
    )
    
    if data.get('action') == 'forward':
        new_inquiry.status = 'forwarded'
        
    db.session.add(new_inquiry)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Inquiry created', 'inquiry': new_inquiry.to_dict()}), 201

@bp.route('/inquiries/num/<string:num>', methods=['GET'])
@jwt_required()
def get_inquiry_by_num(num):
    inquiry = Inquiry.query.filter_by(inquiry_number=num).first_or_404()
    return jsonify(inquiry.to_dict())

@bp.route('/inquiries/num/<string:num>/status', methods=['PUT'])
@jwt_required()
def update_status_by_num(num):
    data = request.get_json()
    inquiry = Inquiry.query.filter_by(inquiry_number=num).first_or_404()
    
    if 'status' in data:
        inquiry.status = data['status']
        db.session.commit()
        
    return jsonify({'success': True, 'message': 'Status updated'})

@bp.route('/inquiries/<int:id>', methods=['GET'])
@jwt_required()
def get_inquiry(id):
    inquiry = Inquiry.query.get_or_404(id)
    return jsonify(inquiry.to_dict())

@bp.route('/inquiries/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_status(id):
    data = request.get_json()
    inquiry = Inquiry.query.get_or_404(id)
    
    if 'status' in data:
        inquiry.status = data['status']
        db.session.commit()
        
    return jsonify({'success': True, 'message': 'Status updated'})

    return jsonify({'success': True, 'message': 'Status updated'})

@bp.route('/inquiries/<int:id>', methods=['PUT'])
@jwt_required()
def update_inquiry(id):
    inquiry = Inquiry.query.get_or_404(id)
    data = request.get_json()
    
    # Update fields allowed
    if 'customerName' in data: inquiry.customer_name = data['customerName']
    if 'phone' in data: inquiry.phone = data['phone']
    if 'email' in data: inquiry.email = data['email']
    if 'serviceType' in data: inquiry.service_type = data['serviceType']
    if 'address' in data: inquiry.address = data['address']
    if 'city' in data: inquiry.city = data['city']
    if 'pincode' in data: inquiry.pincode = data['pincode']
    if 'notes' in data: inquiry.notes = data['notes']
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Inquiry updated'})

@bp.route('/inquiries/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_inquiry(id):
    inquiry = Inquiry.query.get_or_404(id)
    db.session.delete(inquiry)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Inquiry deleted'})

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    today = Inquiry.query.count() # Mocking daily count for now as total
    pending = Inquiry.query.filter_by(status='pending').count()
    forwarded = Inquiry.query.filter_by(status='forwarded').count()
    closed = Inquiry.query.filter_by(status='closed').count()
    
    return jsonify({
        'today': today,
        'pending': pending,
        'forwarded': forwarded,
        'closed': closed,
        'chart_data': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'data': [0, 0, 0, 0, 0, 0, 0]
        }
    })
