from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), default="User")  # User or Administrator
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship("Transaction", backref="user", lazy=True)
    login_logs = db.relationship("LoginLog", backref="user", lazy=True)

class Transaction(db.Model):
    __tablename__ = "transactions"
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_time = db.Column(db.DateTime, default=datetime.utcnow)
    device_id = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # P2P, P2M
    account_age_days = db.Column(db.Integer, nullable=False)
    
    # Cybersecurity Results
    risk_score = db.Column(db.Float, nullable=False)  # 0 to 100
    risk_level = db.Column(db.String(10), nullable=False)  # Low, Medium, High
    is_fraud = db.Column(db.Integer, nullable=False)  # 0 = Legitimate, 1 = Fraud
    prediction_model = db.Column(db.String(30), nullable=False)  # Random Forest, etc.
    
    # Relationships
    alerts = db.relationship("Alert", backref="transaction", cascade="all, delete-orphan", lazy=True)

class LoginLog(db.Model):
    __tablename__ = "login_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=False)
    device_agent = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # Success, Failed

class Alert(db.Model):
    __tablename__ = "alerts"
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # Velocity, IP_Blacklist, Model_Detection, etc.
    severity = db.Column(db.String(10), nullable=False)  # Low, Medium, High
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)

class SuspiciousIP(db.Model):
    __tablename__ = "suspicious_ips"
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    flagged_at = db.Column(db.DateTime, default=datetime.utcnow)
