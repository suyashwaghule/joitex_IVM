from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from .config import get_config

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Use provided config or auto-detect from environment
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # CORS Configuration
    cors_origins = getattr(config_class, 'CORS_ORIGINS', '*')
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

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
        from . import models
        from . import models_job
        from . import models_inventory
        from . import models_network
        from . import models_finance
        from . import models_sales
        from . import models_service
        
        db.create_all()

    return app
