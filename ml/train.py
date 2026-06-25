import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from generate_data import generate_upi_dataset

# Configuration
DATA_PATH = "ml/upi_transactions.csv"
MODELS_DIR = "ml/models"

def preprocess_data(df):
    print("Preprocessing data and engineering features...")
    
    # Copy DataFrame
    data = df.copy()
    
    # 1. Extract Hour from Transaction Time
    data["Transaction Time"] = pd.to_datetime(data["Transaction Time"])
    data["Hour"] = data["Transaction Time"].dt.hour
    
    # 2. Extract IP features (is it a private local IP or a public IP?)
    # Local IPs in our synthetic dataset start with '192.168.'
    data["Is_Private_IP"] = data["IP Address"].apply(lambda ip: 1 if ip.startswith("192.168.") else 0)
    
    # 3. Categorical Encodings
    # Transaction Type: P2P=0, P2M=1
    data["Txn_Type_Encoded"] = data["Transaction Type"].map({"P2P": 0, "P2M": 1}).fillna(0).astype(int)
    
    # Location and Device ID mapping (using dictionaries to ensure consistency during inference)
    locations = sorted(data["Location"].unique().tolist())
    location_map = {loc: idx for idx, loc in enumerate(locations)}
    data["Location_Encoded"] = data["Location"].map(location_map).fillna(-1).astype(int)
    
    devices = sorted(data["Device ID"].unique().tolist())
    device_map = {dev: idx for idx, dev in enumerate(devices)}
    data["Device_Encoded"] = data["Device ID"].map(device_map).fillna(-1).astype(int)
    
    # Keep encoding mappings for saving
    mappings = {
        "locations": location_map,
        "devices": device_map
    }
    
    # Define features and target
    feature_cols = [
        "Transaction Amount", 
        "Hour", 
        "Is_Private_IP", 
        "Txn_Type_Encoded", 
        "Location_Encoded", 
        "Device_Encoded", 
        "Account Age"
    ]
    
    X = data[feature_cols]
    y = data["Fraud Status"]
    
    return X, y, mappings

def train_and_evaluate():
    # Check if dataset exists, if not generate it
    if not os.path.exists(DATA_PATH):
        generate_upi_dataset()
        
    df = pd.read_csv(DATA_PATH)
    
    # Preprocess
    X, y, mappings = preprocess_data(df)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"Training set size: {X_train.shape[0]} | Testing set size: {X_test.shape[0]}")
    
    # Model 1: Logistic Regression
    print("\n--- Training Logistic Regression ---")
    lr = LogisticRegression(random_state=42, class_weight='balanced')
    lr.fit(X_train_scaled, y_train)
    y_pred_lr = lr.predict(X_test_scaled)
    y_prob_lr = lr.predict_proba(X_test_scaled)[:, 1]
    
    print(classification_report(y_test, y_pred_lr))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_prob_lr):.4f}")
    
    # Model 2: Decision Tree
    print("\n--- Training Decision Tree ---")
    dt = DecisionTreeClassifier(random_state=42, class_weight='balanced', max_depth=8)
    dt.fit(X_train_scaled, y_train)
    y_pred_dt = dt.predict(X_test_scaled)
    y_prob_dt = dt.predict_proba(X_test_scaled)[:, 1]
    
    print(classification_report(y_test, y_pred_dt))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_prob_dt):.4f}")
    
    # Model 3: Random Forest
    print("\n--- Training Random Forest ---")
    rf = RandomForestClassifier(random_state=42, class_weight='balanced', n_estimators=100, max_depth=10)
    rf.fit(X_train_scaled, y_train)
    y_pred_rf = rf.predict(X_test_scaled)
    y_prob_rf = rf.predict_proba(X_test_scaled)[:, 1]
    
    print(classification_report(y_test, y_pred_rf))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_prob_rf):.4f}")
    
    # Save directory
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Save the models, scaler and mappings
    with open(f"{MODELS_DIR}/lr_model.pkl", "wb") as f:
        pickle.dump(lr, f)
    with open(f"{MODELS_DIR}/dt_model.pkl", "wb") as f:
        pickle.dump(dt, f)
    with open(f"{MODELS_DIR}/rf_model.pkl", "wb") as f:
        pickle.dump(rf, f)
    with open(f"{MODELS_DIR}/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open(f"{MODELS_DIR}/mappings.pkl", "wb") as f:
        pickle.dump(mappings, f)
        
    print("\nModels and preprocessing artifacts successfully trained and saved!")
    
    # Write metrics to a dictionary for reporting
    metrics = {
        "lr": {
            "accuracy": accuracy_score(y_test, y_pred_lr),
            "precision": precision_score(y_test, y_pred_lr),
            "recall": recall_score(y_test, y_pred_lr),
            "f1": f1_score(y_test, y_pred_lr),
            "roc_auc": roc_auc_score(y_test, y_prob_lr)
        },
        "dt": {
            "accuracy": accuracy_score(y_test, y_pred_dt),
            "precision": precision_score(y_test, y_pred_dt),
            "recall": recall_score(y_test, y_pred_dt),
            "f1": f1_score(y_test, y_pred_dt),
            "roc_auc": roc_auc_score(y_test, y_prob_dt)
        },
        "rf": {
            "accuracy": accuracy_score(y_test, y_pred_rf),
            "precision": precision_score(y_test, y_pred_rf),
            "recall": recall_score(y_test, y_pred_rf),
            "f1": f1_score(y_test, y_pred_rf),
            "roc_auc": roc_auc_score(y_test, y_prob_rf)
        }
    }
    
    with open(f"{MODELS_DIR}/metrics.pkl", "wb") as f:
        pickle.dump(metrics, f)
        
    return metrics

if __name__ == "__main__":
    train_and_evaluate()
