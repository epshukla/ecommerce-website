from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Register blueprints
    from app.routes import auth, products, cart, orders, admin, payments, wishlist, coupons, addresses, uploads

    app.register_blueprint(auth.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(cart.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(payments.bp)
    app.register_blueprint(wishlist.bp)
    app.register_blueprint(coupons.bp)
    app.register_blueprint(addresses.bp)
    app.register_blueprint(uploads.bp)

    # Create upload folder if it doesn't exist
    import os
    from app.config.upload_config import UPLOAD_FOLDER, PRODUCT_UPLOAD_FOLDER
    os.makedirs(PRODUCT_UPLOAD_FOLDER, exist_ok=True)

    return app
