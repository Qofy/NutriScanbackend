FROM python:3.13-slim

# Install system dependencies for OpenCV/YOLO
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    poppler-utils \
    libpq5 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create a simple Python startup script
RUN cat > /app/run.py << 'EOF'
import os
import sys
import subprocess

port = os.getenv("PORT", "8000")
print(f"🚀 Starting gunicorn on port {port}...")
sys.stdout.flush()

os.execvp("gunicorn", [
    "gunicorn",
    "nutriscan.wsgi",
    "--bind", f"0.0.0.0:{port}",
    "--workers", "1",
    "--timeout", "300",
    "--keep-alive", "75",
    "--access-logfile", "-",
    "--error-logfile", "-"
])
EOF

# Start using Python script
CMD ["python", "/app/run.py"]
