from app import create_app

app = create_app()

if __name__ == "__main__":
    # Runs the web application locally on port 5000
    print("UPI Transaction Fraud Detection System - Starting web service...")
    print("Default operator credentials: admin / admin123")
    app.run(debug=True, host="127.0.0.1", port=5000)
