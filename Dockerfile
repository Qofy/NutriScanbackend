FROM python:3.13-slim

# Install system dependencies including libGL for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run migrations and start server
CMD python manage.py migrate && gunicorn nutriscan.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 300 --keep-alive 75
