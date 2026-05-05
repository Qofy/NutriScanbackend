# NutriScan Backend - Deployment Checklist

Use this checklist before deploying to production.

## Pre-Deployment Review

### Code Quality
- [ ] All tests pass: `python manage.py test`
- [ ] No console errors or warnings
- [ ] Code follows Django conventions
- [ ] Documentation is complete
- [ ] No hardcoded passwords or secrets

### Security
- [ ] `DEBUG = False` in production settings
- [ ] `SECRET_KEY` is random and strong
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] HTTPS enforced in production
- [ ] CORS origins restricted to your frontend domain
- [ ] No sensitive data in git commits
- [ ] `.env` file excluded from git
- [ ] Database password is strong
- [ ] API rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] CSRF protection enabled
- [ ] SQL injection protection (Django ORM handles this)

### Database
- [ ] Database migration tested on production database
- [ ] Database backups configured
- [ ] Database indexes optimized
- [ ] Initial data seeded (optional: `seed_foods.py`)

### Static Files & Media
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Media uploads path writable by server
- [ ] File upload size limits set
- [ ] Malicious file upload protection implemented
- [ ] Old media files cleanup scheduled

---

## Infrastructure Setup

### Server Environment

#### Option 1: Heroku (Easiest)
```bash
# Install Heroku CLI
heroku login

# Create app
heroku create nutriscan-backend

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set DATABASE_URL="postgresql://..."

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
heroku run python manage.py seed_foods
```

#### Option 2: AWS/DigitalOcean/Linode (More Control)
```bash
# On server:
sudo apt-get update
sudo apt-get install python3 python3-pip postgresql nginx

# Clone repo
git clone <repo-url> /app
cd /app

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start with Gunicorn
gunicorn nutriscan.wsgi:application --bind 0.0.0.0:8000
```

#### Option 3: Docker
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "nutriscan.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://...
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=nutriscan
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Database

#### PostgreSQL Setup
```bash
# On server
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb nutriscan
sudo -u postgres createuser nutruser
sudo -u postgres psql -c "ALTER USER nutruser WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE nutriscan TO nutruser;"
```

#### Update settings.py
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nutriscan',
        'USER': 'nutruser',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### Backups
```bash
# Backup database
pg_dump -U nutruser nutriscan > backup.sql

# Restore from backup
psql -U nutruser nutriscan < backup.sql

# Auto-backup (add to crontab)
0 2 * * * pg_dump -U nutruser nutriscan > /backups/backup_$(date +\%Y\%m\%d).sql
```

### Web Server (Nginx)

```nginx
# /etc/nginx/sites-available/nutriscan
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Client upload size
    client_max_body_size 10M;

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL Certificate (Let's Encrypt)
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
```

### Process Manager (Systemd)

```ini
# /etc/systemd/system/gunicorn.service
[Unit]
Description=Gunicorn application server for NutriScan
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/app
ExecStart=/app/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    nutriscan.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

---

## Environment Variables

### Production .env
```
# Django
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://nutruser:password@localhost:5432/nutriscan

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Firebase (if using)
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=...

# ML Models
YOLO_MODEL_PATH=yolov8n.pt
NLP_MODEL_NAME=bert-base-uncased

# Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## Performance Optimization

### Caching
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Database Optimization
```python
# Use select_related for foreign keys
recommendations = Recommendation.objects.select_related('user')

# Use prefetch_related for reverse foreign keys
medical_reports = MedicalReport.objects.prefetch_related('health_info')

# Add database indexes
class UserHealthProfile(models.Model):
    user = models.OneToOneField(..., db_index=True)
```

### API Response Caching
```python
from rest_framework.decorators import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def get_recommendations(request):
    ...
```

---

## Monitoring & Logging

### Logging Setup
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/nutriscan/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### Error Tracking (Sentry)
```bash
pip install sentry-sdk
```

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False
)
```

### Health Check Endpoint
```python
# Add to urls.py
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now()
    })

urlpatterns = [
    path('health/', health_check),
    ...
]
```

---

## Post-Deployment Verification

### Testing
- [ ] Test all API endpoints from frontend
- [ ] Test file uploads (images, PDFs)
- [ ] Test database operations
- [ ] Test authentication/session
- [ ] Test CORS headers
- [ ] Performance test with load testing tool

### Monitoring
- [ ] Server CPU/memory usage
- [ ] Database response times
- [ ] API response times
- [ ] Error rates
- [ ] Uptime/downtime tracking

### User Testing
- [ ] Food analysis flow
- [ ] Medical report upload
- [ ] Recommendations generation
- [ ] Profile management
- [ ] Daily tracking

---

## Maintenance Tasks

### Daily
- [ ] Monitor error logs
- [ ] Check server resources
- [ ] Verify application status

### Weekly
- [ ] Review performance metrics
- [ ] Check for security updates
- [ ] Backup database

### Monthly
- [ ] Update dependencies (carefully)
- [ ] Review and optimize slow queries
- [ ] Analyze user feedback
- [ ] Plan feature improvements

### Quarterly
- [ ] Security audit
- [ ] Performance optimization
- [ ] Database maintenance (VACUUM, ANALYZE)
- [ ] Update SSL certificates (auto with Let's Encrypt)

---

## Rollback Plan

If deployment fails:

```bash
# Stop current version
sudo systemctl stop gunicorn

# Switch to previous version
git checkout previous-version
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate  # Or rollback migrations

# Restart
sudo systemctl start gunicorn

# Verify
curl https://yourdomain.com/health/
```

---

## Success Criteria

- [ ] API responds to requests (< 500ms)
- [ ] Database queries optimized (< 100ms)
- [ ] File uploads working (< 5 seconds)
- [ ] YOLO detection working
- [ ] NLP processing working
- [ ] No 5xx errors in logs
- [ ] SSL certificate valid
- [ ] CORS headers correct
- [ ] Database backups working
- [ ] Monitoring alerts configured

---

## Support & Resources

- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- Nginx Docs: https://nginx.org/en/docs/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Gunicorn Docs: https://gunicorn.org/
- Let's Encrypt: https://letsencrypt.org/

---

## Emergency Contacts

- Server Admin: [your-email]
- Database Admin: [your-email]
- API Support: [your-email]
- On-Call: [rotation-schedule]

---

This checklist ensures your NutriScan backend is production-ready and secure! 🚀
