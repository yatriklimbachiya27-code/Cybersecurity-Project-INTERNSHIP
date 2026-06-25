FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8080

# Expose the port Vercel uses
EXPOSE 8080

# Start the Flask app with gunicorn
# Assumes the Flask app instance is named `app` in run.py
CMD ["gunicorn", "-b", "0.0.0.0:${PORT}", "run:app"]
