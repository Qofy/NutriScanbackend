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

# Start gunicorn - migrations happen during import, that's normal
CMD ["gunicorn", "nutriscan.wsgi", "--bind=0.0.0.0:8000", "--workers=1", "--timeout=300", "--keep-alive=75", "--access-logfile=-", "--error-logfile=-"]
