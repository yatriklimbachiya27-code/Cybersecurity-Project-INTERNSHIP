from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Transaction, LoginLog, Alert, SuspiciousIP
from app.fraud_engine import FraudEngine
from datetime import datetime
import uuid

# Initialize Fraud Engine
fraud_engine = FraudEngine()

# Login Manager custom loader check
from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Authentication Routes ---

def get_client_ip():
    # Helper to get IP address from request
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr or "127.0.0.1"
    return ip

def get_user_agent():
    return request.headers.get("User-Agent", "Unknown Device")

def log_login_attempt(user_id, status):
    log = LoginLog(
        user_id=user_id,
        ip_address=get_client_ip(),
        device_agent=get_user_agent()[:250],
        status=status
    )
    db.session.add(log)
    db.session.commit()


from flask import current_app as app

# Define routes on application context or directly. In Flask __init__.py we imported routes.
# Let's write the route functions decorated with app.route.

# Because flask app is initialized in create_app, we can register routes directly using the current_app's path, 
# or import routes in create_app. Since we import routes inside the create_app context in __init__.py, 
# we can use the `current_app` or import from `flask import current_app as app`. 
# Wait, a cleaner Flask pattern when not using Blueprints is to import `db` and register directly with `app` (current_app).
# Let's write the routing functions and hook them using `@app.route` or similar. Since we are inside `with app.app_context()` in `__init__.py`, 
# we can just use `@app.route` if we import `current_app`!
# Let's check how the import works:
# `from flask import current_app as app`
# And then:
# `@app.route('/')`
# Yes, this works beautifully in Flask because `current_app` acts as a proxy for the active application instance.

@app.route("/login", methods=["GET", "POST"])
def auth_login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            log_login_attempt(user.id, "Success")
            flash(f"Welcome back, {username}! Access granted.", "success")
            return redirect(url_for("dashboard"))
        else:
            if user:
                log_login_attempt(user.id, "Failed")
            flash("Invalid credentials! Security log recorded.", "danger")
            
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def auth_register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role", "User")
        
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash("Username or Email already registered!", "danger")
        else:
            hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")
            new_user = User(username=username, email=email, password_hash=hashed_pw, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("auth_login"))
            
    return render_template("register.html")

@app.route("/logout")
@login_required
def auth_logout():
    logout_user()
    flash("Successfully logged out. Session terminated.", "info")
    return redirect(url_for("auth_login"))

# --- Dashboard & Core System Routes ---

@app.route("/")
@login_required
def dashboard():
    # Transaction counts
    total_txns = Transaction.query.count()
    fraud_txns = Transaction.query.filter_by(is_fraud=1).count()
    active_alerts = Alert.query.filter_by(is_resolved=False).count()
    blocked_ips = SuspiciousIP.query.count()
    
    # Recent items
    recent_transactions = Transaction.query.order_by(Transaction.transaction_time.desc()).limit(8).all()
    recent_alerts = Alert.query.order_by(Alert.created_at.desc()).limit(5).all()
    recent_logins = LoginLog.query.order_by(LoginLog.login_time.desc()).limit(5).all()
    
    # Calculate stats
    fraud_ratio = (fraud_txns / total_txns * 100) if total_txns > 0 else 0.0
    
    # Risk summary
    high_risk_count = Transaction.query.filter_by(risk_level="High").count()
    med_risk_count = Transaction.query.filter_by(risk_level="Medium").count()
    low_risk_count = Transaction.query.filter_by(risk_level="Low").count()
    
    return render_template(
        "dashboard.html",
        total_txns=total_txns,
        fraud_txns=fraud_txns,
        active_alerts=active_alerts,
        blocked_ips=blocked_ips,
        recent_transactions=recent_transactions,
        recent_alerts=recent_alerts,
        recent_logins=recent_logins,
        fraud_ratio=round(fraud_ratio, 2),
        high_risk_count=high_risk_count,
        med_risk_count=med_risk_count,
        low_risk_count=low_risk_count
    )

@app.route("/monitor", methods=["GET", "POST"])
@login_required
def monitor_txn():
    # Mock data choices for dropdowns
    users_list = User.query.all()
    devices = ["DV_SAMS_01", "DV_APPL_02", "DV_ONEP_03", "DV_XIAO_04", "DV_REAL_05", "DV_VIVO_06", "DV_OPPO_07", "DV_NEW_99"]
    locations = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Pune", "Jaipur", "Lucknow", "Goa"]
    txn_types = ["P2P", "P2M"]
    models = ["Random Forest", "Decision Tree", "Logistic Regression"]
    
    # Auto-generate a Transaction ID
    generated_txn_id = f"TXN{uuid.uuid4().hex[:8].upper()}"
    
    # Default parameters for form
    client_ip = get_client_ip()
    if client_ip == "127.0.0.1" or client_ip.startswith("::"):
        # Put a typical local IP range
        client_ip = "192.168.1.105"
        
    if request.method == "POST":
        txn_id = request.form.get("transaction_id")
        tgt_user_id = int(request.form.get("user_id", current_user.id))
        amount = float(request.form.get("amount", 0.0))
        device_id = request.form.get("device_id")
        ip_addr = request.form.get("ip_address")
        loc = request.form.get("location")
        t_type = request.form.get("transaction_type")
        acc_age = int(request.form.get("account_age", 30))
        model_choice = request.form.get("model_choice")
        
        # Prepare transaction payload
        txn_payload = {
            "amount": amount,
            "time": datetime.utcnow(),
            "device_id": device_id,
            "ip_address": ip_addr,
            "location": loc,
            "txn_type": t_type,
            "account_age": acc_age,
            "model_choice": model_choice
        }
        
        # Run through Fraud Engine
        evaluation = fraud_engine.evaluate_transaction(txn_payload, tgt_user_id)
        
        # Create Transaction Database Object
        new_txn = Transaction(
            transaction_id=txn_id,
            user_id=tgt_user_id,
            amount=amount,
            transaction_time=txn_payload["time"],
            device_id=device_id,
            ip_address=ip_addr,
            location=loc,
            transaction_type=t_type,
            account_age_days=acc_age,
            risk_score=evaluation["risk_score"],
            risk_level=evaluation["risk_level"],
            is_fraud=evaluation["is_fraud"],
            prediction_model=model_choice
        )
        db.session.add(new_txn)
        db.session.commit()
        
        # Trigger Alerts if Risk is Elevated
        if evaluation["risk_level"] in ["Medium", "High"]:
            severity = evaluation["risk_level"]
            alert_type = "Cyber_Anomaly"
            
            # Sub-categories
            if "Suspicious IP" in evaluation["alert_message"]:
                alert_type = "Blacklisted_IP_Access"
            elif "Velocity" in evaluation["alert_message"]:
                alert_type = "Velocity_Anomaly"
            elif "New Device" in evaluation["alert_message"]:
                alert_type = "Unrecognized_Device"
                
            new_alert = Alert(
                transaction_id=new_txn.id,
                alert_type=alert_type,
                severity=severity,
                message=evaluation["alert_message"],
                is_resolved=False
            )
            db.session.add(new_alert)
            
            # If high risk and IP not blacklisted yet, auto-blacklist the IP
            if evaluation["risk_level"] == "High":
                ip_blocked = SuspiciousIP.query.filter_by(ip_address=ip_addr).first()
                if not ip_blocked:
                    db.session.add(SuspiciousIP(
                        ip_address=ip_addr,
                        reason=f"Auto-blocked: Triggered High Risk Transaction {txn_id} (Score: {evaluation['risk_score']})"
                    ))
            db.session.commit()
            
        flash(f"Transaction processed! Status: {evaluation['risk_level']} Risk (Score: {evaluation['risk_score']})", 
              "warning" if evaluation["risk_level"] in ["Medium", "High"] else "success")
        
        return redirect(url_for("dashboard"))

    return render_template(
        "monitor.html",
        users=users_list,
        devices=devices,
        locations=locations,
        txn_types=txn_types,
        models=models,
        generated_txn_id=generated_txn_id,
        client_ip=client_ip
    )

@app.route("/alerts")
@login_required
def alerts_list():
    active_alerts = Alert.query.filter_by(is_resolved=False).order_by(Alert.created_at.desc()).all()
    resolved_alerts = Alert.query.filter_by(is_resolved=True).order_by(Alert.created_at.desc()).limit(20).all()
    return render_template("alerts.html", active_alerts=active_alerts, resolved_alerts=resolved_alerts)

@app.route("/alerts/resolve/<int:alert_id>", methods=["POST"])
@login_required
def resolve_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.is_resolved = True
    db.session.commit()
    flash(f"Alert ID #{alert_id} successfully marked as resolved.", "success")
    return redirect(url_for("alerts_list"))

@app.route("/report")
@login_required
def system_reports():
    transactions = Transaction.query.order_by(Transaction.transaction_time.desc()).all()
    suspicious_ips = SuspiciousIP.query.order_by(SuspiciousIP.flagged_at.desc()).all()
    
    # Calculate some dashboard summaries
    total = len(transactions)
    frauds = sum(1 for t in transactions if t.is_fraud == 1)
    avg_amt = (sum(t.amount for t in transactions) / total) if total > 0 else 0
    
    return render_template(
        "report.html",
        transactions=transactions,
        suspicious_ips=suspicious_ips,
        total_count=total,
        fraud_count=frauds,
        avg_amount=round(avg_amt, 2)
    )

@app.route("/ips/add", methods=["POST"])
@login_required
def add_blocked_ip():
    ip = request.form.get("ip_address")
    reason = request.form.get("reason", "Manually flagged threat IP")
    
    if ip:
        existing = SuspiciousIP.query.filter_by(ip_address=ip).first()
        if existing:
            flash(f"IP {ip} is already in the blocklist.", "warning")
        else:
            db.session.add(SuspiciousIP(ip_address=ip, reason=reason))
            db.session.commit()
            flash(f"IP {ip} successfully added to the blocklist.", "success")
    return redirect(url_for("system_reports"))

@app.route("/ips/remove/<int:ip_id>", methods=["POST"])
@login_required
def remove_blocked_ip(ip_id):
    ip_rec = SuspiciousIP.query.get_or_404(ip_id)
    ip_addr = ip_rec.ip_address
    db.session.delete(ip_rec)
    db.session.commit()
    flash(f"IP {ip_addr} successfully removed from the blocklist.", "info")
    return redirect(url_for("system_reports"))

# --- JSON API Endpoints for Chart.js charts ---

@app.route("/api/stats")
@login_required
def api_stats():
    # 1. Monthly or Daily Transaction distribution
    transactions = Transaction.query.all()
    
    # 2. Risk levels distribution
    high = sum(1 for t in transactions if t.risk_level == "High")
    med = sum(1 for t in transactions if t.risk_level == "Medium")
    low = sum(1 for t in transactions if t.risk_level == "Low")
    
    # 3. Model Accuracy or Predictions distribution
    model_counts = {}
    for t in transactions:
        model_counts[t.prediction_model] = model_counts.get(t.prediction_model, 0) + 1
        
    # 4. Transaction types P2P vs P2M
    p2p = sum(1 for t in transactions if t.transaction_type == "P2P")
    p2m = sum(1 for t in transactions if t.transaction_type == "P2M")
    
    # 5. Fraud counts by Model
    model_fraud = {"Random Forest": 0, "Decision Tree": 0, "Logistic Regression": 0}
    for t in transactions:
        if t.is_fraud == 1:
            model_fraud[t.prediction_model] = model_fraud.get(t.prediction_model, 0) + 1
            
    # Assemble data
    return jsonify({
        "risk_distribution": {
            "labels": ["Low Risk", "Medium Risk", "High Risk"],
            "data": [low, med, high]
        },
        "transaction_types": {
            "labels": ["P2P (Peer-to-Peer)", "P2M (Peer-to-Merchant)"],
            "data": [p2p, p2m]
        },
        "model_performance": {
            "labels": list(model_fraud.keys()),
            "data": list(model_fraud.values())
        }
    })
