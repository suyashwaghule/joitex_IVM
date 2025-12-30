from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Role
from app.models_sales import BroadbandPlan
import bcrypt

bp = Blueprint('admin', __name__)

@bp.route('/plans', methods=['GET'])
@jwt_required()
def get_plans():
    plans = BroadbandPlan.query.all()
    return jsonify([p.to_dict() for p in plans])

@bp.route('/plans', methods=['POST'])
@jwt_required()
def create_plan():
    data = request.json
    plan = BroadbandPlan(
        name=data['name'],
        speed_mbps=data['speed'],
        price_monthly=data['price'],
        data_limit_gb=0 if data.get('data_limit') == 'unlimited' else int(data.get('data_limit_val', 0)),
        description=data.get('features', ''),
        # 'type' is not in model, ignoring for now or could append to name
        is_active=True
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify(plan.to_dict()), 201

@bp.route('/plans/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_plan(id):
    plan = BroadbandPlan.query.get_or_404(id)
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'message': 'Plan deleted'})

@bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    roles = Role.query.all()
    # If no roles exist (db reset), return [] or seed in-memory system roles could be an option, 
    # but we'll stick to db.
    return jsonify([r.to_dict() for r in roles])

@bp.route('/roles', methods=['POST'])
@jwt_required()
def create_role():
    data = request.json
    if Role.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Role already exists'}), 400
        
    role = Role(
        name=data['name'],
        description=data.get('description'),
        color=data.get('color', '#1976d2'),
        permissions=data.get('permissions', [])
    )
    db.session.add(role)
    db.session.commit()
    return jsonify(role.to_dict()), 201

@bp.route('/roles/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_role(id):
    role = Role.query.get_or_404(id)
    if role.is_system:
        return jsonify({'error': 'Cannot delete system roles'}), 400
    
    # Check if users are assigned to this role (by name since User.role is string)
    if User.query.filter_by(role=role.name).first():
        return jsonify({'error': 'Cannot delete role assigned to users'}), 400
        
    db.session.delete(role)
    db.session.commit()
    return jsonify({'message': 'Role deleted'})


@bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    data = request.json
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'User already exists'}), 400

    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = User(
        name=data['name'],
        email=data['email'],
        password_hash=hashed,
        role=data['role'],
        permissions=[], # Default permissions based on role can be handled here if needed
        portals=[data['role']] # Default portal access based on role
    )
    
    if data['role'] == 'admin':
        user.portals = ['admin', 'callcenter', 'sales', 'salesexec', 'engineer', 'inventory', 'network', 'finance']
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@bp.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.role == 'admin' and User.query.filter_by(role='admin').count() == 1:
         return jsonify({'error': 'Cannot delete the last admin'}), 400
         
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    total = User.query.count()
    # Assuming 'active' status logic, but model might not have status field based on seed. 
    # Checking seed.py: User model has 'role', 'name', 'email', 'permissions', 'portals'. No 'status'.
    # We will assume all users are active for now or add a status field. 
    # For now, let's treat all as active.
    active = total 
    inactive = 0
    online = 1 # Mocking online count
    
    return jsonify({
        'total': total,
        'active': active,
        'inactive': inactive,
        'online': online
    })
