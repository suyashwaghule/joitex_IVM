from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Register blueprints
    # Register blueprints
    from .routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from .routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    from .routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

    from .routes.callcenter import bp as callcenter_bp
    app.register_blueprint(callcenter_bp, url_prefix='/api/callcenter')

    from .routes.engineer import bp as engineer_bp
    app.register_blueprint(engineer_bp, url_prefix='/api/engineer')

    from .routes.finance import finance_bp
    app.register_blueprint(finance_bp, url_prefix='/api/finance')

    from .routes.inventory import inventory_bp
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')

    from .routes.network import network_bp
    app.register_blueprint(network_bp, url_prefix='/api/network')

    from .routes.sales import sales_bp
    app.register_blueprint(sales_bp, url_prefix='/api/sales')

    from .routes.sales_exec import sales_exec_bp
    app.register_blueprint(sales_exec_bp, url_prefix='/api/salesexec')

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
