# NutriScan API Documentation

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently using Django Session Authentication. Include your session cookie with requests.

---

## Food Recognition API

### Analyze Food Image

**POST** `/food/analysis/analyze/`

Upload a food image for analysis using YOLO.

**Request:**
```bash
curl -X POST http://localhost:8000/api/food/analysis/analyze/ \
  -F "image=@food.jpg" \
  -H "Cookie: sessionid=your-session-id"
```

**Request Body (multipart/form-data):**
```
image: <binary image file>
health_profile: {"conditions": ["diabetes"], "allergens": []}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "image": "/media/food_analysis/2026/04/15/food.jpg",
  "uploaded_at": "2026-04-15T10:30:00Z",
  "recognized_items": [
    {
      "name": "Apple",
      "confidence": 0.95
    },
    {
      "name": "Carrot",
      "confidence": 0.92
    }
  ],
  "nutritional_info": {
    "apple": {
      "calories": 95,
      "protein": 0.5,
      "carbs": 25,
      "fat": 0.3,
      "fiber": 4.4
    }
  },
  "safety_level": "safe",
  "confidence_score": 0.935,
  "analysis_result": {
    "detection": {...},
    "nutrition": {...},
    "safety_reason": "This food appears to be safe for your health profile"
  }
}
```

### Get Recent Food Analyses

**GET** `/food/analysis/recent/?limit=10`

Retrieve recent food analyses for the current user.

**Query Parameters:**
- `limit` (optional): Number of results to return (default: 10)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "uploaded_at": "2026-04-15T10:30:00Z",
    "recognized_items": [...],
    "safety_level": "safe"
  }
]
```

### Search Food Items

**GET** `/food/items/search/?q=apple`

Search for food items in the database.

**Query Parameters:**
- `q` (required): Search query

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Apple",
    "calories": 95,
    "protein": 0.5,
    "carbs": 25,
    "fat": 0.3,
    "fiber": 4.4,
    "vitamins": {"C": "8.4mg"},
    "minerals": {"potassium": "195mg"},
    "allergens": []
  }
]
```

---

## Medical Processing API

### Upload Medical Report

**POST** `/medical/reports/upload/`

Upload and process a medical report (PDF or image).

**Request:**
```bash
curl -X POST http://localhost:8000/api/medical/reports/upload/ \
  -F "document=@report.pdf" \
  -H "Cookie: sessionid=your-session-id"
```

**Request Body (multipart/form-data):**
```
document: <binary PDF or image file>
```

**Response (201 Created):**
```json
{
  "id": 1,
  "document": "/media/medical_reports/2026/04/15/report.pdf",
  "uploaded_at": "2026-04-15T10:30:00Z",
  "status": "completed",
  "extracted_data": {
    "conditions": [
      {
        "condition": "diabetes",
        "confidence": 0.85,
        "severity": "high"
      }
    ],
    "allergens": [
      {
        "allergen": "peanuts",
        "confidence": 0.80,
        "severity": "moderate"
      }
    ],
    "dietary_restrictions": [...]
  },
  "health_info": [
    {
      "condition_name": "diabetes",
      "confidence": 0.85,
      "description": "Detected from medical document",
      "severity": "high"
    }
  ],
  "allergies": [
    {
      "allergen": "peanuts",
      "reaction_type": "unknown",
      "severity": "moderate",
      "confidence": 0.80
    }
  ],
  "dietary_restrictions": [
    {
      "restriction": "high_sugar_foods",
      "reason": "Based on diabetes diagnosis",
      "recommendation": "Avoid high sugar foods"
    }
  ]
}
```

### Get Recent Medical Reports

**GET** `/medical/reports/recent/?limit=10`

Retrieve recent medical reports.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "uploaded_at": "2026-04-15T10:30:00Z",
    "status": "completed"
  }
]
```

### Get Health Summary

**GET** `/medical/reports/health_summary/`

Get aggregated health information from all medical reports.

**Response (200 OK):**
```json
{
  "conditions": [
    {
      "condition": "diabetes",
      "severity": "high",
      "confidence": 0.85
    }
  ],
  "allergens": [
    {
      "allergen": "peanuts",
      "severity": "moderate",
      "confidence": 0.80
    }
  ],
  "dietary_restrictions": [
    {
      "restriction": "high_sugar_foods",
      "reason": "Based on diabetes diagnosis",
      "recommendation": "Avoid high sugar foods"
    }
  ],
  "report_count": 1
}
```

---

## Recommendations API

### Get Personalized Recommendations

**GET** `/recommendations/personalized/?conditions=diabetes&conditions=hypertension&allergens=peanuts`

Get recommendations based on health conditions and allergens.

**Query Parameters:**
- `conditions` (optional): List of health conditions
- `allergens` (optional): List of allergens

**Response (200 OK):**
```json
{
  "recommendations": [
    {
      "food_item": "Carrots",
      "emoji": "🥕",
      "description": "Rich in beta-carotene and vitamin A...",
      "conditions": ["diabetes", "heart_disease"],
      "benefit": "Low glycemic index helps maintain stable blood sugar levels",
      "severity": "safe",
      "nutrition": {
        "calories": 41,
        "protein": 0.9,
        "carbs": 10,
        "fiber": 2.8
      }
    }
  ],
  "count": 5,
  "profile": {
    "conditions": ["diabetes", "hypertension"],
    "allergens": ["peanuts"]
  }
}
```

### Get Recommendations from Medical Reports

**GET** `/recommendations/health_based/`

Get recommendations based on extracted health data from medical reports.

**Response (200 OK):**
```json
{
  "recommendations": [...],
  "count": 8,
  "source": "medical_reports",
  "profile": {
    "conditions": ["diabetes", "hypertension"],
    "allergens": ["peanuts"]
  }
}
```

### Get Personalized Tips

**GET** `/recommendations/tips/?conditions=diabetes&conditions=hypertension`

Get personalized health tips based on conditions.

**Response (200 OK):**
```json
{
  "tips": [
    {
      "title": "Blood Sugar Management",
      "description": "Monitor carbohydrate intake and pair carbs with protein and fiber"
    },
    {
      "title": "Sodium Control",
      "description": "Limit salt intake to less than 2300mg per day"
    }
  ],
  "profile": {
    "conditions": ["diabetes", "hypertension"],
    "allergens": []
  }
}
```

### Track Recommendation Action

**POST** `/recommendations/track_action/`

Track user interaction with a recommendation.

**Request Body:**
```json
{
  "recommendation_id": 1,
  "action": "viewed"
}
```

**Action Types:**
- `viewed`: User viewed the recommendation
- `saved`: User saved the recommendation
- `dismissed`: User dismissed the recommendation
- `followed`: User followed the recommendation

**Response (201 Created):**
```json
{
  "id": 1,
  "recommendation": {...},
  "viewed_at": "2026-04-15T10:30:00Z",
  "action": "viewed"
}
```

---

## User Profile API

### Get Current User

**GET** `/profile/user/me/`

Get current authenticated user information.

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Get Health Profile

**GET** `/profile/health/`

Get user's health profile.

**Response (200 OK):**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "age": 35,
  "gender": "male",
  "height": 180,
  "weight": 75,
  "bmi": 23.15,
  "activity_level": "moderately_active",
  "dietary_preferences": ["vegetarian"],
  "allergies": ["peanuts"],
  "health_conditions": ["diabetes"],
  "dietary_restrictions": ["high_sugar_foods"],
  "medications": ["Metformin"],
  "goals": ["weight_management", "blood_sugar_control"],
  "created_at": "2026-04-10T08:00:00Z",
  "updated_at": "2026-04-15T10:30:00Z"
}
```

### Create Health Profile

**POST** `/profile/health/`

Create a new health profile.

**Request Body:**
```json
{
  "age": 35,
  "gender": "male",
  "height": 180,
  "weight": 75,
  "activity_level": "moderately_active",
  "dietary_preferences": ["vegetarian"],
  "allergies": ["peanuts"],
  "health_conditions": ["diabetes"],
  "dietary_restrictions": ["high_sugar_foods"],
  "medications": ["Metformin"],
  "goals": ["weight_management"]
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user": {...},
  "age": 35,
  ...
}
```

### Update Health Profile

**PUT** `/profile/health/`

Update health profile.

**Request Body:** (same as create, partial updates allowed)

**Response (200 OK):**
```json
{...updated profile...}
```

### Update Health Conditions

**POST** `/profile/health/conditions/`

Update health conditions.

**Request Body:**
```json
{
  "conditions": ["diabetes", "hypertension"]
}
```

**Response (200 OK):**
```json
{...updated profile...}
```

### Update Allergies

**POST** `/profile/health/allergies/`

Update allergies.

**Request Body:**
```json
{
  "allergens": ["peanuts", "shellfish"]
}
```

**Response (200 OK):**
```json
{...updated profile...}
```

### Get Today's Daily Tracking

**GET** `/profile/daily-tracking/today/`

Get today's daily tracking entry.

**Response (200 OK):**
```json
{
  "id": 1,
  "user": 1,
  "date": "2026-04-15",
  "meals": [
    {
      "name": "Breakfast",
      "items": ["Oatmeal", "Banana"],
      "time": "08:00"
    }
  ],
  "water_intake": 2.5,
  "exercise_minutes": 30,
  "notes": "Feeling good today",
  "mood": "excellent"
}
```

### Create Daily Tracking

**POST** `/profile/daily-tracking/`

Create a new daily tracking entry.

**Request Body:**
```json
{
  "meals": [
    {
      "name": "Breakfast",
      "items": ["Oatmeal", "Banana"],
      "time": "08:00"
    }
  ],
  "water_intake": 2.5,
  "exercise_minutes": 30,
  "notes": "Feeling great",
  "mood": "excellent"
}
```

**Response (201 Created):**
```json
{...tracking entry...}
```

### Get Saved Foods

**GET** `/profile/saved-foods/?limit=10`

Get user's saved foods.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "food_name": "Apple",
    "nutritional_info": {...},
    "safety_level": "safe",
    "saved_at": "2026-04-15T10:30:00Z"
  }
]
```

### Save a Food

**POST** `/profile/saved-foods/`

Save a food for later reference.

**Request Body:**
```json
{
  "food_name": "Apple",
  "nutritional_info": {
    "calories": 95,
    "protein": 0.5,
    "carbs": 25
  },
  "safety_level": "safe"
}
```

**Response (201 Created):**
```json
{...saved food...}
```

### Search Saved Foods

**GET** `/profile/saved-foods/search/?q=apple`

Search saved foods.

**Query Parameters:**
- `q` (required): Search query

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "No image provided"
}
```

### 404 Not Found
```json
{
  "error": "Health profile not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "An unexpected error occurred"
}
```

---

## Rate Limiting

Currently not implemented. Can be added using Django REST framework's throttling.

## CORS

Enabled for frontend development at `http://localhost:3000`

## Content Type

All responses are in `application/json` format.
