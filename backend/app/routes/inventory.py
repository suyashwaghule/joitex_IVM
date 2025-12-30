from flask import Blueprint, jsonify, request
from app import db
from app.models_inventory import InventoryItem, StockTransaction, StockRequest
from app.models_finance import Vendor
from app.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
import json

inventory_bp = Blueprint('inventory', __name__)

# --- Stats ---
@inventory_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    items = InventoryItem.query.all()
    total_items = sum(i.quantity for i in items)
    total_skus = len(items)
    
    low_stock_count = sum(1 for i in items if i.quantity <= i.min_stock_level and i.quantity > 0)
    out_of_stock_count = sum(1 for i in items if i.quantity == 0)
    
    pending_requests = StockRequest.query.filter_by(status='pending').count()
    
    today_start = datetime.combine(date.today(), datetime.min.time())
    todays_movements = StockTransaction.query.filter(StockTransaction.created_at >= today_start).count()
    
    categories = {}
    for i in items:
        if i.category not in categories:
            categories[i.category] = {'count': 0, 'value': 0}
        categories[i.category]['count'] += i.quantity
        categories[i.category]['value'] += (i.quantity * i.unit_price)
    
    chart_data = {
        'labels': list(categories.keys()),
        'quantity': [d['count'] for d in categories.values()],
        'value': [d['value'] for d in categories.values()]
    }

    return jsonify({
        'kpi': {
            'total_stock': total_items,
            'total_skus': total_skus,
            'low_stock': low_stock_count,
            'out_of_stock': out_of_stock_count,
            'pending_requests': pending_requests,
            'todays_movements': todays_movements
        },
        'chart_data': chart_data
    })

# --- Catalog / Items ---
@inventory_bp.route('/items', methods=['GET'])
@jwt_required()
def get_items():
    category = request.args.get('category')
    status = request.args.get('status')
    
    query = InventoryItem.query
    if category:
        query = query.filter_by(category=category)
    
    items = query.all()
    results = [i.to_dict() for i in items]
    
    if status:
        if status == 'instock':
            results = [i for i in results if i['status'] == 'in_stock']
        elif status == 'low':
            results = [i for i in results if i['status'] == 'low_stock']
        elif status == 'out':
            results = [i for i in results if i['status'] == 'out_of_stock']
            
    return jsonify(results)

@inventory_bp.route('/items', methods=['POST'])
@jwt_required()
def create_item():
    data = request.json
    item = InventoryItem(
        sku=data['sku'],
        name=data['name'],
        category=data['category'],
        description=data.get('description'),
        unit_price=data.get('unit_price', 0),
        quantity=data.get('quantity', 0),
        min_stock_level=data.get('min_stock_level', 10)
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@inventory_bp.route('/items/<int:id>', methods=['GET'])
@jwt_required()
def get_item(id):
    item = InventoryItem.query.get_or_404(id)
    return jsonify(item.to_dict())

# --- Requests ---
@inventory_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_requests():
    status = request.args.get('status')
    query = StockRequest.query
    if status:
        query = query.filter_by(status=status)
    reqs = query.order_by(StockRequest.created_at.desc()).all()
    return jsonify([r.to_dict() for r in reqs])

@inventory_bp.route('/requests', methods=['POST'])
@jwt_required()
def create_request():
    data = request.json
    req = StockRequest(
        request_number=f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        engineer_name=data.get('engineer_name', 'Unknown'),
        job_id=data.get('job_id'),
        items_requested=json.dumps(data['items']),
        priority=data.get('priority', 'normal'),
        status='pending'
    )
    db.session.add(req)
    db.session.commit()
    return jsonify(req.to_dict()), 201

@inventory_bp.route('/requests/<int:id>/approve', methods=['POST'])
@jwt_required()
def approve_request(id):
    req = StockRequest.query.get_or_404(id)
    if req.status != 'pending':
        return jsonify({'error': 'Request already processed'}), 400
    
    current_user_id = get_jwt_identity()
    items = json.loads(req.items_requested)
    
    # Check stock first
    for item_req in items:
        # Try finding by name or SKU
        item = InventoryItem.query.filter((InventoryItem.name == item_req['name']) | (InventoryItem.sku == item_req.get('sku'))).first()
        if not item:
            return jsonify({'error': f"Item '{item_req['name']}' not found in inventory"}), 400
        qty = int(item_req.get('qty', item_req.get('quantity', 0)))
        if item.quantity < qty:
            return jsonify({'error': f"Insufficient stock for {item.name}. Available: {item.quantity}"}), 400

    # Deduct stock and log
    for item_req in items:
        item = InventoryItem.query.filter((InventoryItem.name == item_req['name']) | (InventoryItem.sku == item_req.get('sku'))).first()
        qty = int(item_req.get('qty', item_req.get('quantity', 0)))
        item.quantity -= qty
        
        tx = StockTransaction(
            item_id=item.id,
            transaction_type='OUT',
            quantity=qty,
            reference=req.request_number,
            performed_by=current_user_id,
            notes=f"Approved request from {req.engineer_name} for Job {req.job_id}"
        )
        db.session.add(tx)

    req.status = 'approved'
    db.session.commit()
    return jsonify(req.to_dict())

@inventory_bp.route('/requests/<int:id>/reject', methods=['POST'])
@jwt_required()
def reject_request(id):
    req = StockRequest.query.get_or_404(id)
    if req.status != 'pending':
        return jsonify({'error': 'Request already processed'}), 400
    req.status = 'rejected'
    db.session.commit()
    return jsonify(req.to_dict())

# --- Transactions ---
@inventory_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    txs = StockTransaction.query.order_by(StockTransaction.created_at.desc()).limit(50).all()
    return jsonify([t.to_dict() for t in txs])

@inventory_bp.route('/receive', methods=['POST'])
@jwt_required()
def receive_stock():
    data = request.json
    current_user_id = get_jwt_identity()
    
    for item_data in data['items']:
        item_id = item_data.get('item_id')
        if not item_id and 'sku' in item_data:
            i_obj = InventoryItem.query.filter_by(sku=item_data['sku']).first()
            if i_obj: item_id = i_obj.id

        item = InventoryItem.query.get(item_id) if item_id else None
        if item:
            qty = int(item_data['quantity'])
            item.quantity += qty
            if 'unit_price' in item_data:
                item.unit_price = float(item_data['unit_price'])
            
            tx = StockTransaction(
                item_id=item.id,
                transaction_type='IN',
                quantity=qty,
                reference=data.get('reference'),
                performed_by=current_user_id,
                notes=data.get('notes')
            )
            db.session.add(tx)
            
    db.session.commit()
    return jsonify({'message': 'Stock received successfully'})

@inventory_bp.route('/issue', methods=['POST'])
@jwt_required()
def issue_stock():
    data = request.json
    current_user_id = get_jwt_identity()
    
    for item_data in data['items']:
        item = InventoryItem.query.get(item_data['item_id'])
        if item:
            qty = int(item_data['quantity'])
            if item.quantity < qty:
                return jsonify({'error': f'Insufficient stock for {item.name}'}), 400
            
            item.quantity -= qty
            
            tx = StockTransaction(
                item_id=item.id,
                transaction_type='OUT',
                quantity=qty,
                reference=data.get('job_id') or 'Direct Issue',
                performed_by=current_user_id,
                notes=f"Issued to {data.get('engineer_name')}"
            )
            db.session.add(tx)
            
    db.session.commit()
    return jsonify({'message': 'Stock issued successfully'})

@inventory_bp.route('/engineers', methods=['GET'])
@jwt_required()
def get_engineers():
    engineers = User.query.filter_by(role='engineer').all()
    return jsonify([{'id': u.id, 'name': u.name} for u in engineers])

@inventory_bp.route('/vendors', methods=['GET'])
@jwt_required()
def get_vendors():
    vendors = Vendor.query.all()
    return jsonify([v.to_dict() for v in vendors])

@inventory_bp.route('/vendors', methods=['POST'])
@jwt_required()
def create_vendor():
    data = request.json
    vendor = Vendor(
        name=data['name'],
        contact_person=data.get('contact_person'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        category=data.get('category')
    )
    db.session.add(vendor)
    db.session.commit()
    return jsonify(vendor.to_dict()), 201
