from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from .. import db, limiter
from ..models import User, UserLog
from datetime import datetime
import bcrypt

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON"}), 400
        
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        # Update user stats
        user.last_login = datetime.utcnow()
        user.last_seen = datetime.utcnow()
        user.is_active = True
        
        # Log activity
        log = UserLog(
            user_id=user.id,
            action='login',
            ip_address=request.remote_addr,
            details='User logged in'
        )
        db.session.add(log)
        db.session.commit()

        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        return jsonify({
            "success": True,
            "access_token": access_token,
            "user": user.to_dict(),
            "redirectUrl": "select-portal.html" # Match frontend expectation
        }), 200
    
    return jsonify({"success": False, "message": "Invalid email or password"}), 401

@bp.route('/register', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def register():
    # Protected endpoint - Admin only
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Admin privileges required"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid JSON"}), 400

    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'user')
    
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400
        
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    new_user = User(
        email=email,
        password_hash=hashed,
        name=name,
        role=role,
        permissions=data.get('permissions', []),
        portals=data.get('portals', [])
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully"}), 201

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user:
        user.last_logout = datetime.utcnow()
        user.last_seen = datetime.utcnow()
        # We don't necessarily set is_active=False here if "active" means "enable/disabled account". 
        # But if "active" means "currently online", then yes.
        # The prompt says "real time active or not". Since HTTP is stateless, "active" usually means "session active".
        # Let's interpret "active" in the table as "Currently Online" status.
        # But `is_active` field in model usually means "Account Enabled".
        # I will use `last_seen` vs `last_logout` to determine "Online" status in frontend.
        # However, updating `last_logout` is key here.
        
        log = UserLog(
            user_id=user.id,
            action='logout',
            ip_address=request.remote_addr,
            details='User logged out'
        )
        db.session.add(log)
        db.session.commit()
    
    return jsonify({"success": True, "message": "Logged out successfully"}), 200
