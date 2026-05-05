# NutriScan Backend - Quick Start Guide

## 1. Setup (5 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings (optional for development)

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# (Optional) Seed food database
python manage.py seed_foods

# Start server
python manage.py runserver 8000
```

## 2. Test the API

### Using cURL

```bash
# 1. Get CSRF token from admin
curl -c cookies.txt http://localhost:8000/admin/

# 2. Login
curl -b cookies.txt -c cookies.txt \
  -d "username=admin&password=yourpassword" \
  http://localhost:8000/admin/login/

# 3. Analyze a food image
curl -b cookies.txt -X POST http://localhost:8000/api/food/analysis/analyze/ \
  -F "image=@test_food.jpg"

# 4. Get recent analyses
curl -b cookies.txt http://localhost:8000/api/food/analysis/recent/
```

### Using Python

```python
import requests
from requests.auth import HTTPBasicAuth

# Create a session
session = requests.Session()

# Login
response = session.post('http://localhost:8000/api/profile/user/me/')

# Upload food image
with open('food.jpg', 'rb') as f:
    files = {'image': f}
    response = session.post(
        'http://localhost:8000/api/food/analysis/analyze/',
        files=files
    )
    print(response.json())
```

## 3. Test with Admin Interface

1. Go to `http://localhost:8000/admin/`
2. Login with your superuser credentials
3. Create test data:
   - Add Health Conditions
   - Add Allergies
   - Add Food Items

## 4. API Endpoints

### Food Recognition
- `POST /api/food/analysis/analyze/` - Analyze food image
- `GET /api/food/analysis/recent/` - Recent analyses
- `GET /api/food/items/search/?q=apple` - Search foods

### Medical Processing
- `POST /api/medical/reports/upload/` - Upload report
- `GET /api/medical/reports/recent/` - Recent reports
- `GET /api/medical/reports/health_summary/` - Health summary

### Recommendations
- `GET /api/recommendations/personalized/` - Get recommendations
- `GET /api/recommendations/health_based/` - Based on medical reports
- `GET /api/recommendations/tips/` - Health tips

### User Profile
- `GET /api/profile/health/` - Get health profile
- `PUT /api/profile/health/` - Update profile
- `POST /api/profile/daily-tracking/` - Create daily tracking
- `GET /api/profile/daily-tracking/today/` - Today's tracking
- `POST /api/profile/saved-foods/` - Save a food

## 5. Troubleshooting

### Port already in use
```bash
python manage.py runserver 8001
```

### Migration errors
```bash
python manage.py migrate --fake-initial
```

### Reset database
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### YOLO model not loading
- Automatically falls back to mock detection
- Model downloads automatically on first use (~130MB)
- For offline use, pre-download: `yolo detect predict model=yolov8n.pt source=test.jpg`

## 6. Environment Variables

For production:
```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgres://user:password@host:port/dbname
```

## 7. Next Steps

- [ ] Connect to frontend (http://localhost:3000)
- [ ] Set up Firebase authentication
- [ ] Deploy to production
- [ ] Configure email notifications
- [ ] Set up monitoring and logging

## 8. Common Commands

```bash
# Create new app
python manage.py startapp myapp

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic --noinput

# Dump data
python manage.py dumpdata > backup.json

# Load data
python manage.py loaddata backup.json
```

## 9. Documentation

- API Documentation: See `API_DOCUMENTATION.md`
- Project README: See `README.md`
- Code comments: Inline documentation in each module

## 10. Support

For issues:
1. Check logs: `python manage.py runserver` (check console output)
2. Check Django admin for data issues
3. Run tests: `python manage.py test`
4. Check CORS settings if frontend requests fail
