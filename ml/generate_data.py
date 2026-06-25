import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_upi_dataset(num_records=10000):
    print(f"Generating {num_records} synthetic UPI transaction records...")
    
    # Base lists of features
    locations = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Pune", "Jaipur", "Lucknow"]
    device_models = ["DV_SAMS_01", "DV_APPL_02", "DV_ONEP_03", "DV_XIAO_04", "DV_REAL_05", "DV_VIVO_06", "DV_OPPO_07"]
    txn_types = ["P2P", "P2M"]  # Peer-to-Peer, Peer-to-Merchant
    
    # Generate mock users
    num_users = 200
    users = [f"USR_{1000 + i}" for i in range(num_users)]
    
    # Generate profile for each user (normal location, normal device, average amount)
    user_profiles = {}
    for user in users:
        user_profiles[user] = {
            "home_location": random.choice(locations),
            "primary_device": random.choice(device_models),
            "avg_amount": random.uniform(100, 3000),
            "account_age": random.randint(10, 1200),
            "ips": [f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(3)]
        }

    data = []
    start_time = datetime.now() - timedelta(days=30)
    
    for i in range(num_records):
        txn_id = f"TXN{100000 + i}"
        user_id = random.choice(users)
        profile = user_profiles[user_id]
        
        # Fraud probability determination (approx 5% base fraud rate)
        # We increase probability under certain cybersecurity threat conditions
        is_fraud = 0
        rand_val = random.random()
        
        # Determine features based on fraud status (normal behavior vs anomalous behavior)
        if rand_val < 0.05:  # Let's generate a fraud record
            is_fraud = 1
            # Fraudulent characteristics:
            # 1. High amount compared to user's average or high absolute amount
            amount = round(random.uniform(15000, 95000), 2)
            # 2. Unusual transaction time (night hours: 1 AM - 5 AM)
            hour = random.choice([0, 1, 2, 3, 4, 5, 23])
            # 3. Mismatched device ID
            device_id = random.choice([d for d in device_models if d != profile["primary_device"]])
            # 4. Unknown IP Address (often mimicking external ranges)
            ip_address = f"{random.randint(103, 107)}.{random.randint(10, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            # 5. Remote/different location
            location = random.choice([loc for loc in locations if loc != profile["home_location"]])
            # 6. Newly created accounts are more prone to fraud
            account_age = random.randint(1, 15)
            txn_type = random.choice(txn_types)
        else:
            # Legitimate characteristics:
            amount = round(abs(np.random.normal(profile["avg_amount"], profile["avg_amount"] * 0.4)) + 10, 2)
            # Clamp amount
            amount = max(5.0, min(amount, 20000.0))
            # Normal daytime/evening hours (6 AM - 11 PM)
            hour = random.randint(6, 22)
            device_id = profile["primary_device"]
            # 5% chance of using a backup device
            if random.random() < 0.05:
                device_id = random.choice(device_models)
            ip_address = random.choice(profile["ips"])
            location = profile["home_location"]
            # 3% chance of travelling
            if random.random() < 0.03:
                location = random.choice(locations)
            account_age = profile["account_age"]
            txn_type = random.choice(txn_types)
            
        # Create timestamp
        days_offset = random.randint(0, 29)
        minutes_offset = random.randint(0, 59)
        seconds_offset = random.randint(0, 59)
        txn_time = start_time + timedelta(days=days_offset, hours=hour, minutes=minutes_offset, seconds=seconds_offset)
        txn_time_str = txn_time.strftime("%Y-%m-%d %H:%M:%S")
        
        data.append({
            "Transaction ID": txn_id,
            "User ID": user_id,
            "Transaction Amount": amount,
            "Transaction Time": txn_time_str,
            "Device ID": device_id,
            "IP Address": ip_address,
            "Location": location,
            "Transaction Type": txn_type,
            "Account Age": account_age,
            "Fraud Status": is_fraud
        })
        
    df = pd.DataFrame(data)
    
    # Save directory verification
    os.makedirs(os.path.dirname("ml/"), exist_ok=True)
    df.to_csv("ml/upi_transactions.csv", index=False)
    print(f"Dataset successfully created and saved to ml/upi_transactions.csv! Shape: {df.shape}")
    print(f"Fraud count: {df['Fraud Status'].sum()} ({df['Fraud Status'].mean() * 100:.2f}%)")

if __name__ == "__main__":
    generate_upi_dataset()
