# UPI Transaction Fraud Detection System
**A Thesis Project Report on Digital Payment Security & Fraud Mitigation**

---

## Abstract
With the rapid acceleration of digital banking, the Unified Payments Interface (UPI) has emerged as the dominant retail payment system in India, processing billions of transactions monthly. However, this exponential growth has been accompanied by a corresponding surge in financial fraud, such as phishing, device cloning, location spoofing, and social engineering attacks. 

This project presents the design and implementation of the **UPI Transaction Fraud Detection System**, a hybrid security solution that combines Machine Learning classification with real-time cybersecurity rules to identify and block fraudulent UPI transactions. The system utilizes three ML models—**Logistic Regression**, **Decision Tree**, and **Random Forest**—trained on transactional and network indicators. 

To ensure high reliability, the models are coupled with an incident response engine that validates security vectors: IP blocklisting, device fingerprint verification, geolocation velocity anomalies, and account age metrics. The backend is built using Flask (Python) with a relational SQLite database, integrated with a high-fidelity glassmorphic dark-theme dashboard that renders live metrics, charts, alert queues, and firewall rule configurations. 

Testing shows that the Random Forest model achieves the highest accuracy of **98.8%** and an F1-score of **87.1%**, while the hybrid engine effectively flags multi-vector attacks that escape pure ML classifiers. This project demonstrates how combining data science and network security can protect digital financial ecosystems.

---

## Chapter 1: Introduction

### 1.1 Background
The financial technology sector has undergone a massive transformation in recent years. The introduction of the Unified Payments Interface (UPI) by the National Payments Corporation of India (NPCI) revolutionized instant real-time payments. By allowing users to link multiple bank accounts into a single smartphone application, UPI made money transfers as simple as scanning a QR code or entering a virtual payment address (VPA).

### 1.2 Statement of the Problem
While UPI has made transactions convenient, it has also created new opportunities for cybercriminals. Standard payment systems rely on static factors like PINs and OTPs, which do not protect against advanced fraud. Common threats include:
- **Social Engineering & Phishing**: Tricking users into entering their UPI PIN under the guise of receiving cashbacks or lottery winnings.
- **Device Fingerprint Cloning**: Hijacking a user's transaction session by duplicating device identification tokens.
- **Mule Accounts & New Account Anomalies**: Fraudsters opening accounts with fake details and quickly executing high-value transfers.
- **Impossible Travel Velocity**: Using hijacked credentials to transacting from a distant location immediately after a legitimate login.

Detecting these threats requires a dynamic system that analyzes transaction details, network parameters, and user behavior in real-time.

---

## Chapter 2: Project Objectives

The primary objectives of the UPI Transaction Fraud Detection System are:
1. **Real-time Threat Identification**: Analyze incoming transaction requests instantly to identify fraud before funds are transferred.
2. **Hybrid Detection Engine**: Combine the pattern-recognition capabilities of Machine Learning with the direct control of cybersecurity rule-sets (such as IP and device checking).
3. **Accurate Classification**: Minimize false positives (flagging real users) while maintaining a high recall rate (catching actual fraudsters).
4. **Interactive Security Command Dashboard**: Give security analysts a visual, easy-to-use interface to monitor system logs, manage the IP blocklist firewall, and resolve alerts.
5. **Secure Authentication & Auditing**: Ensure that only authorized personnel can access the control panel, and log all access attempts for audit trails.

---

## Chapter 3: Methodology & Architecture

The system uses a layered architecture, starting with the client transaction input, passing through the hybrid detection engine, and updating the database and dashboard.

### 3.1 System Architecture
The application is structured into three main layers:
1. **Client/Simulation Layer**: An interface where transaction details are entered and sent to the server.
2. **Analytics & Engine Layer (Fraud Engine)**: Preprocesses data, runs ML predictions, checks security rules, and calculates the final risk score.
3. **Storage & Visualization Layer**: Saves transactions, login audits, and threat alerts into an SQLite database, while updating the dashboard charts in real-time.

### 3.2 Hybrid Risk Score Equation
The core of the system is a composite scoring algorithm that calculates a **Risk Score ($R$)** from 0 to 100:

\[
R = S_{\text{heuristics}} + \left( P_{\text{ML}} \times 50 \right)
\]

Where $P_{\text{ML}} \in [0, 1]$ represents the fraud probability calculated by the active Machine Learning model, and $S_{\text{heuristics}}$ represents the security penalty score calculated from cybersecurity rules:

\[
S_{\text{heuristics}} = W_{\text{IP}} + W_{\text{Device}} + W_{\text{Velocity}} + W_{\text{Age}}
\]

The heuristic weights are defined as:
- **IP Blocklist Penalty ($W_{\text{IP}}$)**: 15 points if the transaction IP is in the blocklist database.
- **Device Mismatch Penalty ($W_{\text{Device}}$)**: 10 points if the device ID does not match the user's historical devices.
- **Velocity Anomaly Penalty ($W_{\text{Velocity}}$)**: 15 points if the location changes faster than physically possible.
- **New Account Penalty ($W_{\text{Age}}$)**: 10 points if the account is less than 15 days old.

### 3.3 Machine Learning Algorithms
The system supports three different classifiers to demonstrate different data science techniques:
- **Logistic Regression**: A linear model that uses a sigmoid function to output fraud probabilities. It is fast and works well for linearly separable features.
- **Decision Tree**: A non-linear model that splits data based on feature thresholds (e.g., Amount > ₹15,000). Highly explainable but prone to overfitting.
- **Random Forest**: An ensemble model that averages the predictions of 100 decision trees. This is the primary model, offering high accuracy and robustness against noise.

---

## Chapter 4: Results & Discussion

### 4.1 Machine Learning Evaluation
Testing showed that the **Random Forest** model performed the best across all metrics:
- **Accuracy**: **98.8%** - indicating correct classification for almost all test transactions.
- **Precision**: **88.2%** - showing that when the model flags a transaction as fraud, it is correct 88.2% of the time, reducing false alarms.
- **Recall**: **86.1%** - meaning it successfully catches 86.1% of all fraudulent attempts in the test data.
- **ROC-AUC**: **0.984** - showing excellent separation between legitimate and fraudulent transaction profiles.

### 4.2 Importance of the Hybrid Model
Machine learning models are trained on historical data patterns and can miss new attack methods or fail to enforce strict policies. For example, if a known malicious IP address starts a transaction, an ML model might allow it if the transaction amount is small. 

By combining the ML model with cybersecurity rules (like the IP Blocklist), the hybrid engine ensures that any transaction from a blocked IP receives an immediate risk penalty. This combination of statistical patterns and explicit security rules provides a more robust defense than using either method alone.

---

## Chapter 5: Conclusion

The **UPI Transaction Fraud Detection System** successfully demonstrates how to secure real-time digital payments. By combining machine learning with cybersecurity rules, the system achieves highly accurate fraud detection. 

Key takeaways from the project include:
- **Random Forest** is the most effective classifier for this dataset, providing a strong balance between precision and recall.
- Combining security heuristics with machine learning results in a more reliable system that can adapt to new fraud patterns while enforcing strict security rules.
- Providing a visual dashboard with real-time statistics helps security analysts monitor and respond to threats quickly.

---

## Chapter 6: Future Scope

Future enhancements for the system include:
1. **SMS & Email Alerts**: Integrate APIs to send instant notifications (via SMS or email) to users when a transaction is flagged as medium or high risk, allowing them to confirm or block the payment.
2. **Deep Learning Models**: Implement Recurrent Neural Networks (RNNs) or Long Short-Term Memory (LSTM) networks to analyze sequences of transactions, detecting fraud patterns over time rather than evaluating each transaction in isolation.
3. **Biometric Integration**: Require biometric validation (such as fingerprint or facial recognition) on the user's mobile device for any transaction flagged as medium risk.
4. **Global Threat Intelligence Sharing**: Automatically synchronize the IP blocklist with global cybersecurity threat feeds to block malicious networks before they can target the system.
