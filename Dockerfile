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

# Create startup script that runs migrations then gunicorn
RUN printf '#!/bin/bash\nset -e\necho "Running migrations..."\npython manage.py migrate --noinput\necho "Starting gunicorn..."\nexec gunicorn nutriscan.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 300 --keep-alive 75 --access-logfile - --error-logfile -\n' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]
