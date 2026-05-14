FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8080

# Start gunicorn (migrations run in release phase via fly.toml)
CMD ["gunicorn", "nutriscan.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60"]
