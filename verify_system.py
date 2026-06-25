import os
import sys
from datetime import datetime

# Add project root to path to ensure relative imports work
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, SuspiciousIP
from app.fraud_engine import FraudEngine

def run_tests():
    print("======================================================================")
    print("       UPI Transaction Fraud Detection System - Core Test Suite       ")
    print("======================================================================\n")
    
    app = create_app()
    
    with app.app_context():
        engine = FraudEngine()
        
        # Get a user (or default admin seeded)
        test_user = User.query.filter_by(username="admin").first()
        if not test_user:
            print("ERROR: Admin user not found in database. Seed failure.")
            return
            
        print(f"Using Test Operator: {test_user.username} (ID: {test_user.id})")
        print(f"IP Blocklist count: {SuspiciousIP.query.count()}\n")
        
        # Test Case 1: Legitimate low amount transaction
        print("--- TEST CASE 1: Typical Legitimate Transaction ---")
        txn_1 = {
            "amount": 450.00,
            "time": datetime.utcnow(),
            "device_id": "DV_SAMS_01",
            "ip_address": "192.168.1.12",
            "location": "Mumbai",
            "txn_type": "P2M",
            "account_age": 250,
            "model_choice": "Random Forest"
        }
        res_1 = engine.evaluate_transaction(txn_1, test_user.id)
        print(f"Payload Amount: INR {txn_1['amount']} | Device: {txn_1['device_id']} | IP: {txn_1['ip_address']}")
        print(f"Result -> Risk Score: {res_1['risk_score']}% | Level: {res_1['risk_level']} | Predicted Fraud: {res_1['is_fraud']}")
        print(f"Message: {res_1['alert_message']}")
        print(f"Verification: {'PASS' if res_1['risk_level'] == 'Low' and res_1['is_fraud'] == 0 else 'FAIL'}\n")
        
        # Test Case 2: Suspicious transaction (Medium Risk)
        print("--- TEST CASE 2: Suspicious Activity (Medium Risk) ---")
        txn_2 = {
            "amount": 14500.00, # higher amount
            "time": datetime.utcnow(),
            "device_id": "DV_NEW_99", # unrecognized device
            "ip_address": "122.160.42.19", # public IP
            "location": "Bengaluru",
            "txn_type": "P2P",
            "account_age": 45,
            "model_choice": "Decision Tree"
        }
        res_2 = engine.evaluate_transaction(txn_2, test_user.id)
        print(f"Payload Amount: INR {txn_2['amount']} | Device: {txn_2['device_id']} | IP: {txn_2['ip_address']}")
        print(f"Result -> Risk Score: {res_2['risk_score']}% | Level: {res_2['risk_level']} | Predicted Fraud: {res_2['is_fraud']}")
        print(f"Rules Flagged: {res_2['rule_flags']}")
        print(f"Message: {res_2['alert_message']}")
        print(f"Verification: {'PASS' if res_2['risk_level'] == 'Medium' else 'FAIL'}\n")
        
        # Test Case 3: Blacklisted IP & High amount (High Risk / Auto-Decline)
        print("--- TEST CASE 3: Blacklisted IP Target & Anomaly (High Risk) ---")
        txn_3 = {
            "amount": 65000.00, # very high amount
            "time": datetime.utcnow(),
            "device_id": "DV_NEW_99",
            "ip_address": "103.45.12.98", # Blacklisted IP seeded in database!
            "location": "Delhi",
            "txn_type": "P2P",
            "account_age": 3, # very new account
            "model_choice": "Logistic Regression"
        }
        res_3 = engine.evaluate_transaction(txn_3, test_user.id)
        print(f"Payload Amount: INR {txn_3['amount']} | Device: {txn_3['device_id']} | IP: {txn_3['ip_address']}")
        print(f"Result -> Risk Score: {res_3['risk_score']}% | Level: {res_3['risk_level']} | Predicted Fraud: {res_3['is_fraud']}")
        print(f"Rules Flagged: {res_3['rule_flags']}")
        print(f"Message: {res_3['alert_message']}")
        print(f"Verification: {'PASS' if res_3['risk_level'] == 'High' and res_3['is_fraud'] == 1 else 'FAIL'}\n")
        
        print("======================================================================")
        print("                 Verification Suite Execution Complete                ")
        print("======================================================================")

if __name__ == "__main__":
    run_tests()
