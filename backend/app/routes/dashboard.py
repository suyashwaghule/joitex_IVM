from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ..models import User, Lead, OLT, Product, db
from sqlalchemy import func

bp = Blueprint('dashboard', __name__)

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    # 1. Total Users
    total_users = User.query.count()

    # 2. Active Leads
    active_leads = Lead.query.filter(Lead.status.in_(['new', 'feasibility', 'in_progress'])).count()

    # 3. Pending Installations
    pending_installs = Lead.query.filter_by(status='in_progress').count()

    # 4. Low Stock Items
    low_stock = Product.query.filter(Product.stock_level <= Product.min_threshold).count()

    # 5. OLTs Online
    online_olts = OLT.query.filter_by(status='online').count()
    total_olts = OLT.query.count()
    olt_display = f"{online_olts}/{total_olts}"

    # OLT Chart Data
    offline_olts = OLT.query.filter_by(status='offline').count()
    maint_olts = OLT.query.filter_by(status='maintenance').count()

    return jsonify({
        "success": True,
        "kpi": {
            "total_users": total_users,
            "active_leads": active_leads,
            "pending_installs": pending_installs,
            "low_stock": low_stock,
            "olts_online": olt_display,
            "licenses_expiring": 0
        },
        "leads_chart": {
            "labels": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            "datasets": [
                {"label": 'New Inquiries', "data": [0, 0, 0, 0, 0, 0, 0], "backgroundColor": 'rgba(25, 118, 210, 0.8)'},
                {"label": 'Feasible', "data": [0, 0, 0, 0, 0, 0, 0], "backgroundColor": 'rgba(13, 148, 136, 0.8)'},
                {"label": 'In Progress', "data": [0, 0, 0, 0, 0, 0, 0], "backgroundColor": 'rgba(249, 115, 22, 0.8)'},
                {"label": 'Installed', "data": [0, 0, 0, 0, 0, 0, 0], "backgroundColor": 'rgba(34, 197, 94, 0.8)'}
            ]
        },
        "olt_chart": {
            "labels": ['Online', 'Offline', 'Maintenance'],
            "data": [online_olts, offline_olts, maint_olts]
        },
        "recent_activity": [],
        "system_alerts": []
    })

@bp.route('/charts/leads', methods=['GET'])
@jwt_required()
def get_leads_chart():
    # Return empty data structure (mock removed)
    return jsonify({
        "labels": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        "datasets": [
            {"label": 'New Inquiries', "data": [0, 0, 0, 0, 0, 0, 0]},
            {"label": 'Feasible', "data": [0, 0, 0, 0, 0, 0, 0]},
            {"label": 'In Progress', "data": [0, 0, 0, 0, 0, 0, 0]},
            {"label": 'Installed', "data": [0, 0, 0, 0, 0, 0, 0]}
        ]
    })

@bp.route('/charts/olts', methods=['GET'])
@jwt_required()
def get_olt_chart():
    online = OLT.query.filter_by(status='online').count()
    offline = OLT.query.filter_by(status='offline').count()
    maintenance = OLT.query.filter_by(status='maintenance').count()

    return jsonify({
        "labels": ['Online', 'Offline', 'Maintenance'],
        "data": [online, offline, maintenance]
    })
