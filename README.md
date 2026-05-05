# NutriScan Backend

Django REST API for the NutriScan AI health assessment system. This backend provides APIs for food image recognition, medical report processing, personalized recommendations, and user profile management.

## Project Structure

```
backend/
├── nutriscan/              # Main Django project configuration
├── food_recognition/       # Food detection & nutritional analysis
├── medical_processing/     # Medical report processing & NLP extraction
├── recommendations/        # Recommendation engine
├── user_profile/          # User health profile management
├── manage.py
├── requirements.txt
└── README.md
```

## Services Overview

### 1. Food Recognition Service (`/api/food/`)
Analyzes food images using YOLO and provides nutritional information.

**Endpoints:**
- `POST /api/food/analysis/analyze/` - Upload and analyze a food image
- `GET /api/food/analysis/recent/` - Get recent food analyses
- `GET /api/food/items/search/` - Search food database

**Features:**
- Food image detection using YOLOv8
- Nutritional information lookup
- Safety evaluation based on health profile
- Analysis history tracking

### 2. Medical Processing Service (`/api/medical/`)
Processes medical documents and extracts health information.

**Endpoints:**
- `POST /api/medical/reports/upload/` - Upload and process medical report
- `GET /api/medical/reports/recent/` - Get recent reports
- `GET /api/medical/reports/health_summary/` - Get health profile summary

**Features:**
- PDF and image document processing
- Health condition extraction
- Allergy detection
- Dietary restriction identification
- Confidence scoring

### 3. Recommendation Engine (`/api/recommendations/`)
Generates personalized dietary recommendations.

**Endpoints:**
- `GET /api/recommendations/personalized/` - Get recommendations for conditions
- `GET /api/recommendations/health_based/` - Get recommendations from medical reports
- `GET /api/recommendations/tips/` - Get personalized health tips
- `POST /api/recommendations/track_action/` - Track user interaction with recommendations

**Features:**
- Health condition-based recommendations
- Allergy filtering
- Personalized tips
- User engagement tracking

### 4. User Profile Service (`/api/profile/`)
Manages user health profiles and daily tracking.

**Endpoints:**
- `GET /api/profile/health/` - Get health profile
- `PUT /api/profile/health/` - Update health profile
- `POST /api/profile/health/conditions/` - Update health conditions
- `POST /api/profile/health/allergies/` - Update allergies
- `GET /api/profile/daily-tracking/` - Get daily tracking records
- `POST /api/profile/daily-tracking/` - Create daily tracking
- `GET /api/profile/daily-tracking/today/` - Get today's tracking
- `GET /api/profile/saved-foods/` - Get saved foods
- `POST /api/profile/saved-foods/` - Save a food
- `GET /api/profile/user/me/` - Get current user info

**Features:**
- Health profile management
- BMI calculation
- Daily tracking (meals, water, exercise, mood)
- Saved foods library

## Setup

### 1. Clone and Install

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

### 4. Run Server

```bash
python manage.py runserver 8000
```

Server will be available at `http://localhost:8000`

## API Documentation

### Authentication

Currently uses Django session authentication. Token-based authentication can be added using Django REST framework's Token Authentication.

### Request Format

```json
{
  "condition": "diabetes",
  "allergen": "peanuts"
}
```

### Response Format

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed"
}
```

### Error Handling

```json
{
  "error": "Error message",
  "status": 400
}
```

## Models

### FoodAnalysis
- User food image analysis results
- Recognized items with confidence scores
- Nutritional information
- Safety evaluation

### MedicalReport
- User medical documents
- Extracted health information
- Processing status
- Related conditions, allergies, restrictions

### Recommendation
- Personalized food recommendations
- Condition-based suggestions
- Nutritional information
- User engagement tracking

### UserHealthProfile
- User health information (age, weight, activity level)
- Health conditions
- Allergies and dietary restrictions
- Goals and preferences

### DailyTracking
- Daily meal tracking
- Water intake
- Exercise minutes
- Mood tracking

## ML Models

### YOLO for Food Detection
- Model: YOLOv8 Nano
- Purpose: Food item detection and recognition
- Falls back to mock detection if model unavailable

### NLP for Medical Documents
- Text extraction from PDFs/images
- Named Entity Recognition for health conditions
- Allergen and restriction detection
- Confidence scoring

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test food_recognition

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn nutriscan.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "nutriscan.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Firebase Integration

To enable Firebase:

1. Create Firebase project
2. Download service account JSON
3. Set environment variables from JSON
4. Uncomment Firebase initialization in settings.py

## Troubleshooting

### YOLO Model Issues
- Ensure `torch` and `torchvision` are correctly installed
- Falls back to mock detection automatically
- Check GPU availability for faster processing

### Medical Document Processing
- Supports PDF and image formats
- Max file size: 10MB
- Ensure PDF libraries are installed

### Database Errors
- Run migrations: `python manage.py migrate`
- Check database permissions
- Verify DATABASE_URL

## Contributing

1. Create a new branch for features
2. Follow Django best practices
3. Write tests for new endpoints
4. Update documentation

## License

MIT License

## Support

For issues and questions, contact the development team.
