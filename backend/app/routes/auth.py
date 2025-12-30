from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from .. import db
from ..models import User
import bcrypt

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        return jsonify({
            "success": True,
            "access_token": access_token,
            "user": user.to_dict(),
            "redirectUrl": "select-portal.html" # Match frontend expectation
        }), 200
    
    return jsonify({"success": False, "message": "Invalid email or password"}), 401

@bp.route('/register', methods=['POST'])
def register():
    # Only for seeding/dev use
    data = request.get_json()
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
