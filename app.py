import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "gaming-site-secret-key-2024")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///gaming_site.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
    
    # Proxy fix for deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    return app

# Create app instance
app = create_app()

# Import models to ensure tables are created
from models import User, Game, Comment, GameReaction, UserBan

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()
    logging.info("Database tables created")
    
    # Create default admin and moderator accounts if they don't exist
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('asdf12345.333'),
            role='admin',
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
    
    moderator = User.query.filter_by(username='moder').first()
    if not moderator:
        moderator = User(
            username='moder',
            email='moderator@example.com',
            password_hash=generate_password_hash('asdf12345.333'),
            role='moderator',
            created_at=datetime.utcnow()
        )
        db.session.add(moderator)
    
    try:
        db.session.commit()
        logging.info("Default accounts created")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating default accounts: {e}")
