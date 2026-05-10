import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

HEALTH_CONDITION_RESTRICTIONS = {
    'diabetes': {
        'avoid': ['pizza', 'sugary drinks', 'soda', 'candy', 'cookies'],
        'prefer': ['salad', 'apple', 'carrot', 'spinach', 'broccoli']
    },
    'hypertension': {
        'avoid': ['pizza', 'salt-heavy foods', 'cured meats', 'fried foods'],
        'prefer': ['salad', 'banana', 'grilled chicken', 'fresh vegetables']
    },
    'allergies': {
        'peanut_allergy': {
            'avoid': ['peanuts', 'peanut butter'],
            'safe': ['apple', 'carrot', 'salad', 'almonds']
        },
        'gluten_allergy': {
            'avoid': ['bread', 'pasta', 'wheat'],
            'safe': ['rice', 'vegetables', 'meat']
        }
    }
}


def get_ollama_nutrition(food_name, confidence):
    """Fetch nutritional data from Ollama Cloud API"""
    try:
        api_key = getattr(settings, 'OLLAMA_API_KEY', None)
        if not api_key or not api_key.strip():
            logger.info('❌ Ollama Cloud API key not configured')
            return None

        logger.info(f'🔍 Trying Ollama Cloud for {food_name}...')

        url = 'https://ollama.com/api/chat'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        prompt = f"""You are a nutritionist. A food item "{food_name}" was detected in an image with {confidence*100:.0f}% confidence.

Provide REALISTIC nutritional information for a typical 100g serving in ONLY this JSON format (no other text):
{{
    "calories": <number>,
    "protein": <grams as decimal>,
    "carbs": <grams as decimal>,
    "fat": <grams as decimal>,
    "fiber": <grams as decimal>,
    "vitamins": {{"vitamin_name": "amount with unit"}},
    "minerals": {{"mineral_name": "amount with unit"}},
    "allergens": [<list of common allergens or empty array>]
}}

Examples:
- For "apple": {{"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.4}}
- For "grilled salmon": {{"calories": 206, "protein": 22, "carbs": 0, "fat": 13, "fiber": 0}}

Return ONLY valid JSON, no markdown, no explanation."""

        payload = {
            'model': 'ministral-3:8b',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'stream': False,
            'temperature': 0.3
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        logger.info(f'Ollama Cloud Response Status: {response.status_code}')
        logger.info(f'Ollama Cloud Response: {response.text[:500]}')

        try:
            data = response.json()
        except Exception as json_err:
            logger.error(f'❌ Ollama Cloud returned non-JSON (status: {response.status_code}): {str(json_err)}')
            logger.error(f'Response text: {response.text[:500]}')
            return None

        logger.info(f'Ollama Cloud Data: {data}')
        response_text = data.get('message', {}).get('content', '').strip()
        logger.info(f'Extracted response text: {response_text[:200]}')

        # Clean up response if it has markdown
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        nutrition_data = json.loads(response_text)
        nutrition_data['source'] = 'Ollama-Cloud'

        logger.info(f'✅ Generated Ollama nutrition for {food_name}: {nutrition_data.get("calories")} cal')
        return nutrition_data

    except json.JSONDecodeError as e:
        logger.error(f'❌ Failed to parse Ollama Cloud response for {food_name}: {str(e)}')
        if 'response_text' in locals():
            logger.error(f'Response text: {response_text[:200]}')
        return None
    except Exception as e:
        logger.error(f'❌ Ollama Cloud API error for {food_name}: {str(e)}', exc_info=True)
        return None

def get_ai_nutrition_estimate(food_name, confidence):
    """Use Claude AI to estimate nutritional values based on food name and detection confidence"""
    try:
        from anthropic import Anthropic

        logger.info(f'🔍 Trying Claude AI for {food_name}...')
        client = Anthropic()

        prompt = f"""You are a nutritionist. A food item "{food_name}" was detected in an image with {confidence*100:.0f}% confidence.

Provide REALISTIC nutritional information for a typical 100g serving in ONLY this JSON format (no other text):
{{
    "calories": <number>,
    "protein": <grams as decimal>,
    "carbs": <grams as decimal>,
    "fat": <grams as decimal>,
    "fiber": <grams as decimal>,
    "vitamins": {{"vitamin_name": "amount with unit"}},
    "minerals": {{"mineral_name": "amount with unit"}},
    "allergens": [<list of common allergens or empty array>]
}}

Examples:
- For "apple": {{"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.4, ...}}
- For "grilled salmon": {{"calories": 206, "protein": 22, "carbs": 0, "fat": 13, "fiber": 0, ...}}

Return ONLY valid JSON, no markdown, no explanation."""

        response = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text.strip()

        # Clean up response if it has markdown
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        nutrition_data = json.loads(response_text)
        nutrition_data['source'] = 'Claude-AI'

        logger.info(f'✅ Generated AI nutrition for {food_name}: {nutrition_data.get("calories")} cal')
        return nutrition_data

    except json.JSONDecodeError as e:
        logger.error(f'❌ Failed to parse Claude AI response for {food_name}: {str(e)}')
        logger.error(f'Response text: {response_text[:200]}')
        return None
    except Exception as e:
        logger.error(f'❌ Claude AI nutrition estimation error for {food_name}: {str(e)}', exc_info=True)
        return None

def get_nutritional_info(food_items):
    """Get nutritional info: try Ollama Cloud → Claude AI"""
    nutrition_data = {}

    for item in food_items:
        food_name = item['name'].lower().strip()
        confidence = item.get('confidence', 0.8)

        logger.info(f'\n📍 Fetching nutrition for "{food_name}" (confidence: {confidence*100:.0f}%)')

        # Try Ollama Cloud API first
        logger.info('1️⃣ Trying Ollama Cloud...')
        ollama_nutrition = get_ollama_nutrition(food_name, confidence)
        if ollama_nutrition:
            nutrition_data[food_name] = ollama_nutrition
            logger.info(f'✅ SUCCESS via Ollama Cloud\n')
            continue

        # Fall back to Claude AI (Anthropic API)
        logger.info('2️⃣ Trying Claude AI (Anthropic)...')
        ai_nutrition = get_ai_nutrition_estimate(food_name, confidence)
        if ai_nutrition:
            nutrition_data[food_name] = ai_nutrition
            logger.info(f'✅ SUCCESS via Claude AI\n')
            continue

        # All sources failed
        logger.error(f'❌ ALL SOURCES FAILED for "{food_name}"\n')
        nutrition_data[food_name] = {
            'status': 'not_found',
            'message': f'Unable to get nutrition for "{item["name"]}"',
            'source': 'None'
        }

    return nutrition_data

def evaluate_safety(food_items, health_profile):
    """Evaluate food safety based on user health conditions and allergies"""
    food_names = [item['name'].lower() for item in food_items]
    conditions = health_profile.get('conditions', [])
    allergens = health_profile.get('allergens', [])

    # Check for restricted foods based on health conditions
    restricted_foods = []
    for condition in conditions:
        if condition.lower() in HEALTH_CONDITION_RESTRICTIONS:
            restricted = HEALTH_CONDITION_RESTRICTIONS[condition.lower()].get('avoid', [])
            restricted_foods.extend(restricted)

    for food in food_names:
        if food in restricted_foods:
            return 'caution', f'This food may not be suitable for {", ".join(conditions)}'

    # Check for allergens in food names (basic string matching)
    for allergen in allergens:
        allergen_lower = allergen.lower()
        for food in food_names:
            if allergen_lower in food:
                return 'danger', f'This food contains {allergen} which you are allergic to'

    return 'safe', 'This food appears to be safe for your health profile'
