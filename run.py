from app import create_app

app = create_app()

if __name__ == "__main__":
    # Production run configuration (used only for local debugging)
    # Vercel will use gunicorn; this block is optional.
    import os
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
