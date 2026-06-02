FROM python:3.13-slim

# Install system dependencies
# - libgl1, libglib2.0-0, libsm6, libxext6, libxrender-dev: OpenCV/YOLO dependencies
# - poppler-utils: PDF processing
# - libpq5, libpq-dev: PostgreSQL client libraries (for psycopg)
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

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create startup script
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo "🚀 Running migrations..."' >> /app/start.sh && \
    echo 'python manage.py migrate' >> /app/start.sh && \
    echo 'echo "✅ Starting gunicorn..."' >> /app/start.sh && \
    echo 'gunicorn nutriscan.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 300 --keep-alive 75 --access-logfile - --error-logfile -' >> /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/app/start.sh"]
