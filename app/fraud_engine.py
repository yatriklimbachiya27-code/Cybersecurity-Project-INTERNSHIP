import os
import pickle
import numpy as np
from datetime import datetime, timedelta
from app.models import Transaction, SuspiciousIP, Alert

# Paths
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "models"))

class FraudEngine:
    def __init__(self):
        self.rf_model = None
        self.dt_model = None
        self.lr_model = None
        self.scaler = None
        self.mappings = None
        self.models_loaded = False
        
        self._load_models()

    def _load_models(self):
        try:
            rf_path = os.path.join(MODELS_DIR, "rf_model.pkl")
            dt_path = os.path.join(MODELS_DIR, "dt_model.pkl")
            lr_path = os.path.join(MODELS_DIR, "lr_model.pkl")
            scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
            mappings_path = os.path.join(MODELS_DIR, "mappings.pkl")
            
            if (os.path.exists(rf_path) and os.path.exists(dt_path) and 
                os.path.exists(lr_path) and os.path.exists(scaler_path) and 
                os.path.exists(mappings_path)):
                
                with open(rf_path, "rb") as f:
                    self.rf_model = pickle.load(f)
                with open(dt_path, "rb") as f:
                    self.dt_model = pickle.load(f)
                with open(lr_path, "rb") as f:
                    self.lr_model = pickle.load(f)
                with open(scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
                with open(mappings_path, "rb") as f:
                    self.mappings = pickle.load(f)
                
                self.models_loaded = True
                print("ML Models loaded successfully from pickle files.")
            else:
                print("ML Model pickle files not found. Running in high-fidelity simulation mode.")
        except Exception as e:
            print(f"Error loading ML models: {e}. Running in simulation mode.")

    def evaluate_transaction(self, txn_data, user_id):
        """
        txn_data keys:
          - amount: float
          - time: datetime object
          - device_id: string
          - ip_address: string
          - location: string
          - txn_type: string (P2P or P2M)
          - account_age: int (days)
          - model_choice: string ("Random Forest", "Decision Tree", "Logistic Regression")
        """
        amount = txn_data.get("amount", 0.0)
        txn_time = txn_data.get("time", datetime.utcnow())
        device_id = txn_data.get("device_id", "")
        ip_address = txn_data.get("ip_address", "")
        location = txn_data.get("location", "")
        txn_type = txn_data.get("txn_type", "P2P")
        account_age = txn_data.get("account_age", 30)
        model_choice = txn_data.get("model_choice", "Random Forest")
        
        # 1. CYBERSECURITY HEURISTIC CHECKS
        security_score = 0
        rule_flags = []
        
        # Rule A: Suspicious IP Blacklist
        ip_flagged = SuspiciousIP.query.filter_by(ip_address=ip_address).first()
        if ip_flagged:
            security_score += 15
            rule_flags.append(f"Suspicious IP Flagged: {ip_flagged.reason}")
            
        # Rule B: Device Verification (New Device check)
        previous_txns = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.transaction_time.desc()).limit(5).all()
        if previous_txns:
            known_devices = [t.device_id for t in previous_txns]
            if device_id not in known_devices:
                security_score += 10
                rule_flags.append("New Device Detected: Transaction initiated from an unrecognized device fingerprint.")
        else:
            # First transaction is allowed, but flag new device lightly
            security_score += 3
            rule_flags.append("New Device Detected: First transaction on account.")
            
        # Rule C: Location Velocity Check (impossible speed travel)
        if previous_txns:
            last_txn = previous_txns[0]
            if last_txn.location != location:
                # Calculate time difference
                time_diff = abs((txn_time - last_txn.transaction_time).total_seconds()) / 60.0 # in minutes
                # If they transacted in a different city in less than 60 minutes, flag velocity anomaly
                if time_diff < 60.0:
                    security_score += 15
                    rule_flags.append(f"Velocity Anomaly: Location changed from {last_txn.location} to {location} in {time_diff:.1f} mins.")
        
        # Rule D: Account Age Penalty
        if account_age < 15:
            security_score += 10
            rule_flags.append(f"New Account Penalty: Account is only {account_age} days old.")
            
        # 2. MACHINE LEARNING PREDICTION (50% weight)
        ml_prob = 0.0
        
        if self.models_loaded:
            try:
                # Preprocess features
                hour = txn_time.hour
                is_private_ip = 1 if ip_address.startswith("192.168.") else 0
                txn_type_encoded = 1 if txn_type == "P2M" else 0
                
                # Encodings map lookup
                loc_map = self.mappings.get("locations", {})
                dev_map = self.mappings.get("devices", {})
                
                loc_encoded = loc_map.get(location, -1)
                dev_encoded = dev_map.get(device_id, -1)
                
                # Assemble feature array
                features = np.array([[
                    amount, 
                    hour, 
                    is_private_ip, 
                    txn_type_encoded, 
                    loc_encoded, 
                    dev_encoded, 
                    account_age
                ]])
                
                features_scaled = self.scaler.transform(features)
                
                # Predict probability
                if model_choice == "Logistic Regression":
                    ml_prob = self.lr_model.predict_proba(features_scaled)[0][1]
                elif model_choice == "Decision Tree":
                    ml_prob = self.dt_model.predict_proba(features_scaled)[0][1]
                else:  # Default to Random Forest
                    ml_prob = self.rf_model.predict_proba(features_scaled)[0][1]
                    
            except Exception as e:
                print(f"ML Inference failed ({e}). Falling back to simulation.")
                ml_prob = self._simulate_ml(amount, txn_time, ip_address, device_id, location, account_age, model_choice)
        else:
            ml_prob = self._simulate_ml(amount, txn_time, ip_address, device_id, location, account_age, model_choice)
            
        # ML contribution to risk score (up to 50 points)
        ml_contribution = ml_prob * 50
        
        # 3. COMPOSITE RISK SCORE CALCULATION
        composite_score = security_score + ml_contribution
        composite_score = min(100.0, max(0.0, composite_score))
        
        # 4. DECISIONING AND ALERTS
        if composite_score > 70.0:
            is_fraud = 1
            risk_level = "High"
            alert_msg = f"CRITICAL: Transaction blocked. {', '.join(rule_flags) if rule_flags else 'ML Model flagged high fraud risk.'}"
        elif composite_score > 35.0:
            is_fraud = 0
            risk_level = "Medium"
            alert_msg = f"WARNING: Suspicious activity flagged. {', '.join(rule_flags) if rule_flags else 'Elevated risk detected.'}"
        else:
            is_fraud = 0
            risk_level = "Low"
            alert_msg = "Transaction verified successfully."
            
        return {
            "risk_score": round(composite_score, 2),
            "risk_level": risk_level,
            "is_fraud": is_fraud,
            "ml_probability": round(ml_prob, 4),
            "alert_message": alert_msg,
            "rule_flags": rule_flags
        }
        
    def _simulate_ml(self, amount, txn_time, ip_address, device_id, location, account_age, model_choice):
        """
        High-fidelity simulation of machine learning model responses to represent 
        model properties (Logistic Regression, Decision Tree, Random Forest) without pickle files.
        """
        # Feature heuristics
        hour = txn_time.hour
        is_private_ip = ip_address.startswith("192.168.")
        is_night = hour in [0, 1, 2, 3, 4, 5, 23]
        
        # Calculate raw threat level (0.0 to 1.0)
        threat = 0.0
        
        # Weighting factors
        if amount > 25000:
            threat += 0.4
        elif amount > 10000:
            threat += 0.2
            
        if is_night:
            threat += 0.2
            
        if not is_private_ip:
            threat += 0.15
            
        if account_age < 15:
            threat += 0.2
        elif account_age < 30:
            threat += 0.1
            
        # Add random noise to simulate model variations
        np.random.seed(int(amount * 100) % 100000)
        noise = np.random.normal(0, 0.05)
        threat = min(1.0, max(0.0, threat + noise))
        
        # Model-specific responses
        if model_choice == "Logistic Regression":
            # Smooth logistic/sigmoid activation
            # L = 1 / (1 + e^-k(x-x0))
            k = 6.0
            x0 = 0.45
            prob = 1.0 / (1.0 + np.exp(-k * (threat - x0)))
            return float(prob)
            
        elif model_choice == "Decision Tree":
            # Hard boundary splits (step-like outputs)
            if threat >= 0.7:
                return 0.95
            elif threat >= 0.45:
                return 0.65
            elif threat >= 0.25:
                return 0.15
            else:
                return 0.01
                
        else:  # Random Forest (Ensemble: average of perturbed trees)
            # Smooth but slightly stepped, robust prediction
            tree_preds = []
            for i in range(5):
                t_noise = np.random.normal(0, 0.1)
                t_threat = min(1.0, max(0.0, threat + t_noise))
                if t_threat >= 0.65:
                    tree_preds.append(0.9)
                elif t_threat >= 0.4:
                    tree_preds.append(0.55)
                else:
                    tree_preds.append(0.05)
            prob = np.mean(tree_preds)
            return float(prob)
