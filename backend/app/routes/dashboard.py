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
            "licenses_expiring": 8 # Mocked
        },
        "leads_chart": {
            "labels": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            "datasets": [
                {"label": 'New Inquiries', "data": [12, 19, 15, 17, 14, 21, 18], "backgroundColor": 'rgba(25, 118, 210, 0.8)'},
                {"label": 'Feasible', "data": [8, 14, 11, 13, 10, 16, 14], "backgroundColor": 'rgba(13, 148, 136, 0.8)'},
                {"label": 'In Progress', "data": [5, 9, 7, 8, 6, 11, 9], "backgroundColor": 'rgba(249, 115, 22, 0.8)'},
                {"label": 'Installed', "data": [3, 6, 5, 6, 4, 8, 7], "backgroundColor": 'rgba(34, 197, 94, 0.8)'}
            ]
        },
        "olt_chart": {
            "labels": ['Online', 'Offline', 'Maintenance'],
            "data": [online_olts, offline_olts, maint_olts]
        },
        "recent_activity": [
            {"initials": "JD", "title": "John Doe", "description": "Activated new customer L-2025-0012", "time_ago": "5m ago"},
            {"initials": "SM", "title": "Sales Manager", "description": "Approved feasibility for inquiry INQ-8821", "time_ago": "12m ago"},
            {"initials": "AE", "title": "Ashok Engineer", "description": "Completed installation at Block B-12", "time_ago": "45m ago"}
        ],
        "system_alerts": [
            {"type": "critical", "title": "OLT Offline", "description": "OLT-Surat-01 is unreachable", "time_ago": "2m ago"},
            {"type": "warning", "title": "Low Stock", "description": "ONT (Dual Band) stock below 10 units", "time_ago": "1h ago"}
        ]
    })

@bp.route('/charts/leads', methods=['GET'])
@jwt_required()
def get_leads_chart():
    # Mock data for chart - replace with aggregation later
    return jsonify({
        "labels": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        "datasets": [
            {"label": 'New Inquiries', "data": [12, 19, 15, 17, 14, 21, 18]},
            {"label": 'Feasible', "data": [8, 14, 11, 13, 10, 16, 14]},
            {"label": 'In Progress', "data": [5, 9, 7, 8, 6, 11, 9]},
            {"label": 'Installed', "data": [3, 6, 5, 6, 4, 8, 7]}
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
