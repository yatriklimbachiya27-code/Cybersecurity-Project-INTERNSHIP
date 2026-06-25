import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize Extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth_login"
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config["SECRET_KEY"] = "cyber_security_upi_secret_key_102938"
    
    # Database path
    db_dir = os.path.abspath(os.path.join(app.root_path, "..", "instance"))
    os.makedirs(db_dir, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(db_dir, 'database.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize plugins
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints or routes (we will import routes inside to avoid circular dependency)
    with app.app_context():
        from app import routes
        db.create_all()
        
        # Seed initial data (Administrator and initial suspicious IPs)
        seed_database()
        
    return app

def seed_database():
    from app.models import User, SuspiciousIP
    from werkzeug.security import generate_password_hash
    
    # 1. Create a default admin user if not exists
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        hashed_password = generate_password_hash("admin123", method="pbkdf2:sha256")
        admin = User(
            username="admin",
            password_hash=hashed_password,
            email="admin@upisecure.org",
            role="Administrator"
        )
        db.session.add(admin)
        print("Admin user seeded successfully (admin / admin123)")
        
    # 2. Add some suspicious IPs if empty
    if SuspiciousIP.query.count() == 0:
        bad_ips = [
            ("103.45.12.98", "Reported phishing IP operating in eastern region"),
            ("185.220.101.5", "Tor exit node linked to automated transaction flood"),
            ("45.227.254.12", "Credential stuffing source targeting banking gateways"),
            ("198.51.100.42", "Suspected emulator-based UPI hijacking cluster"),
            ("91.241.19.102", "Known malicious proxy server location")
        ]
        for ip, reason in bad_ips:
            db.session.add(SuspiciousIP(ip_address=ip, reason=reason))
        print("Initial suspicious IPs seeded successfully")
        
    db.session.commit()
