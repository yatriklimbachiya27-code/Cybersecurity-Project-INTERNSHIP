# UPI Transaction Fraud Detection System

A complete Cybersecurity and Machine Learning-driven system designed to monitor, detect, and mitigate fraudulent activities in Unified Payments Interface (UPI) transactions. This project utilizes a hybrid detection engine combining scikit-learn models (Logistic Regression, Decision Tree, Random Forest) with cybersecurity heuristics (such as firewall IP blocklisting, device fingerprint verification, geolocation velocity tracking, and account age metrics) to compute a real-time risk score.

---

## Key Features
1. **User Authentication**: Secure operator login/registration console with password hashing (`pbkdf2:sha256`) and login auditing logs.
2. **Transaction Monitor**: Simulator interface to inject transaction payloads (amount, IP, device, geolocation, account age) and choose the active ML classifier.
3. **Hybrid Fraud Detection Engine**: Composite Risk Score (0-100) calculated using a weighted system: 50% from machine learning probabilities and 50% from cybersecurity rules.
4. **Firewall IP Blocklist**: Dynamic blocklist console enabling administrators to blacklist suspect threat IPs and block transactions in real-time.
5. **Real-time Incident Alerts Feed**: Displays Medium and High-risk warnings with incident-response resolution options.
6. **Aesthetic Web Interface**: Dark-themed, glassmorphic UI using custom CSS variables, backdrop-blur components, dynamic icons (Lucide), and visual reporting charts (Chart.js).

---

## Technology Stack
- **Backend Framework**: Flask (Python)
- **Database ORM**: Flask-SQLAlchemy (SQLite3)
- **Machine Learning**: Scikit-Learn, Pandas, NumPy
- **Frontend Layer**: HTML5, Vanilla CSS3 (Glassmorphism design), Vanilla JS
- **Visual Charts**: Chart.js (CDN)
- **UI Icons**: Lucide Icons (CDN)

---

## Installation & Setup Guide

### 1. Prerequisites
Ensure you have **Python 3.8** or higher installed on your system. You can verify this by running:
```bash
python --version
```

### 2. Extract Project Files
Navigate into the root project directory:
```bash
cd upi_fraud_detection
```

### 3. Initialize Virtual Environment (Recommended)
Create and activate a virtual environment to manage dependencies locally:
- **Windows**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
Install all required libraries using `pip`:
```bash
pip install -r requirements.txt
```

### 5. Generate Dataset & Train ML Models
Run the training script to generate the synthetic transaction dataset (10,000 records) and compile/evaluate the machine learning models:
```bash
python ml/train.py
```
This generates the CSV dataset in `ml/upi_transactions.csv` and serializes the trained classifiers and scalers to the `ml/models/` directory.

### 6. Start the Web Server
Launch the Flask development server:
```bash
python run.py
```
The server will initialize the SQLite database (`instance/database.db`), seed default administrator credentials, and run the service.

Open your browser and navigate to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## Operating Credentials
- **Default Administrator Username**: `admin`
- **Default Administrator Password**: `admin123`

---

## Core System Verification
You can execute the offline test suite to verify that the Fraud Detection Engine operates correctly without booting the web server:
```bash
python verify_system.py
```
This script injects three mock transaction payloads (Legitimate, Suspicious, and High-Risk/Blocklisted) through the analytics engine and validates that risk level categories are mapped correctly.
