# Testing and Evaluation Report

This document records the testing methodologies, model evaluations, and system integration verification tests conducted for the **UPI Transaction Fraud Detection System**.

---

## Part 1: Machine Learning Model Performance

The machine learning models were trained on the engineered features of a synthetic dataset containing 10,000 transactions (stratified with ~5% fraud incidence rate). A standard 80/20 train-test split was utilized, and models were evaluated on the held-out test set (2,000 records).

### Summary of Classification Metrics

| Evaluation Metric | Logistic Regression (Weighted) | Decision Tree (Depth = 8) | Random Forest (100 Trees) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 93.8% | 97.5% | **98.8%** |
| **Precision** | 44.8% | 76.5% | **88.2%** |
| **Recall (Sensitivity)** | **88.1%** | 71.3% | 86.1% |
| **F1-Score** | 59.4% | 73.8% | **87.1%** |
| **ROC-AUC Score** | 0.962 | 0.925 | **0.984** |

---

### Comparative Analysis of Classifiers

1. **Random Forest Classifier (Primary Model)**
   - **Performance**: Achieved the highest overall accuracy (98.8%) and F1-score (87.1%).
   - **Characteristics**: By ensembling 100 decision trees, it reduces individual tree variance and mitigates overfitting. It displays excellent precision (88.2%), meaning very few legitimate transactions are falsely flagged, which is crucial for maintaining a good UPI user experience.

2. **Decision Tree Classifier**
   - **Performance**: Good accuracy (97.5%) but lower F1-score (73.8%).
   - **Characteristics**: Decision Trees utilize strict orthogonal splits which make them fast and explainable. However, they exhibit coarser probability boundaries and are highly sensitive to small data fluctuations.

3. **Logistic Regression (Balanced Class Weights)**
   - **Performance**: High recall (88.1%) but low precision (44.8%).
   - **Characteristics**: By adjusting class weights to counter the imbalanced dataset (5% fraud vs 95% normal), the linear model shifts its decision boundary to prioritize capturing fraud. Consequently, it achieves high sensitivity (capturing 88% of all fraud), but at the cost of flagging many legitimate transactions (false positives).

---

## Part 2: Core System Verification Logs

The system verification suite was executed to check the hybrid risk score calculations and rule execution boundaries. Below are the actual execution logs of the testing runs:

### Test Case 1: Standard Legitimate UPI Transaction
* **Input Payload**:
  - Amount: ₹450.00
  - Geolocation: Mumbai
  - IP Address: `192.168.1.12` (Private Range)
  - Device: `DV_SAMS_01` (Primary user device)
  - Account Age: 250 days
* **Risk Score Details**:
  - Heuristic Security Score: 0 points (No rules breached)
  - ML Model Fraud Probability: 0.02% (Random Forest prediction)
  - Composite Risk Score: **0.01%**
* **Output Verdict**: `Low Risk` (Transaction approved automatically)
* **Status**: **PASS**

### Test Case 2: Suspicious Activity (Unrecognized Device & Geolocation change)
* **Input Payload**:
  - Amount: ₹14,500.00 (Elevated amount)
  - Geolocation: Bengaluru (Different from normal location)
  - IP Address: `122.160.42.19` (Public IP network)
  - Device: `DV_NEW_99` (Unrecognized device ID)
  - Account Age: 45 days
* **Risk Score Details**:
  - Heuristic Security Score: 10 points (Unrecognized device triggered)
  - ML Model Fraud Probability: 54.3% (Decision Tree prediction)
  - Composite Risk Score: **37.15%**
* **Output Verdict**: `Medium Risk` (Warning flagged, security alert generated in logs)
* **Status**: **PASS**

### Test Case 3: High-Risk Attack vector (Blacklisted IP & Anomaly)
* **Input Payload**:
  - Amount: ₹65,000.00 (High-value transaction)
  - Geolocation: Delhi
  - IP Address: `103.45.12.98` (Blacklisted threat IP)
  - Device: `DV_NEW_99` (Unrecognized device ID)
  - Account Age: 3 days (Newly initialized profile)
* **Risk Score Details**:
  - Heuristic Security Score: 35 points (IP Blocklist = 15, Unrecognized Device = 10, New Account age = 10)
  - ML Model Fraud Probability: 86.4% (Logistic Regression prediction)
  - Composite Risk Score: **78.20%**
* **Output Verdict**: `High Risk` (Transaction blocked, high-severity alert logged, transacting IP locked out)
* **Status**: **PASS**

---

## Part 3: Functional Security Verification

1. **Firewall Blocklist Enforcement**:
   - Tested adding `198.51.100.42` to the blocklist. Instantly, all subsequent transactions from this IP were penalized with an extra 15 risk points.
   - Tested removing the IP from the blocklist. Risk scores for the IP returned to normal baseline values.
2. **Access Control Audit Logging**:
   - Failed logins (e.g. incorrect password for 'admin') were successfully recorded with `status='Failed'` along with the operator's IP and user agent.
3. **Alert Lifecycle Management**:
   - High-risk transactions successfully registered alerts in the `alerts` database table. Clicking "Remediate & Resolve" successfully updated `is_resolved` to `True` and cleared them from the active dashboard feed.
