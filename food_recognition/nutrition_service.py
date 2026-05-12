import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def get_food_restrictions_from_ollama(condition_name, severity='unknown', confidence=0.5):
    """Use Ollama to generate food restrictions for a health condition"""
    try:
        api_key = getattr(settings, 'OLLAMA_API_KEY', None)
        if not api_key or not api_key.strip():
            logger.info('❌ Ollama API key not configured for restrictions')
            return None

        logger.info(f'🔍 Getting food restrictions from Ollama for: {condition_name}')

        url = 'https://ollama.com/api/chat'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        prompt = f"""You are a nutritionist. A patient has the following health condition:

Condition: {condition_name}
Severity: {severity}
Confidence: {confidence*100:.0f}%

Generate a list of foods this patient should AVOID and foods they should PREFER for this condition.

Return ONLY a JSON object (no markdown, no other text) with this exact structure:
{{
    "avoid": ["food1", "food2", "food3", ...],
    "prefer": ["food1", "food2", "food3", ...]
}}

Be specific and practical with real food names."""

        payload = {
            'model': 'ministral-3:8b',
            'messages': [{'role': 'user', 'content': prompt}],
            'stream': False,
            'temperature': 0.3
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            content = data.get('message', {}).get('content', '').strip()
            try:
                restrictions = json.loads(content)
                logger.info(f'✅ Got Ollama restrictions for {condition_name}')
                return restrictions
            except json.JSONDecodeError:
                logger.warning(f'Failed to parse Ollama response for {condition_name}')
                return None
        else:
            logger.warning(f'Ollama API error: {response.status_code}')
            return None
    except Exception as e:
        logger.warning(f'Ollama restrictions error for {condition_name}: {e}')
        return None

def get_food_restrictions_from_claude(condition_name, severity='unknown', confidence=0.5):
    """Use Claude to generate food restrictions for a health condition"""
    try:
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        if not api_key or not api_key.strip():
            logger.info('❌ Claude API key not configured for restrictions')
            return None

        logger.info(f'🔍 Getting food restrictions from Claude for: {condition_name}')

        url = 'https://api.anthropic.com/v1/messages'
        headers = {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }

        prompt = f"""You are a nutritionist. A patient has the following health condition:

Condition: {condition_name}
Severity: {severity}
Confidence: {confidence*100:.0f}%

Generate a list of foods this patient should AVOID and foods they should PREFER for this condition.

Return ONLY a JSON object (no markdown, no other text) with this exact structure:
{{
    "avoid": ["food1", "food2", "food3", ...],
    "prefer": ["food1", "food2", "food3", ...]
}}

Be specific and practical with real food names."""

        payload = {
            'model': 'claude-opus-4-1',
            'max_tokens': 500,
            'messages': [{'role': 'user', 'content': prompt}]
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', [{}])[0].get('text', '').strip()
            try:
                restrictions = json.loads(content)
                logger.info(f'✅ Got Claude restrictions for {condition_name}')
                return restrictions
            except json.JSONDecodeError:
                logger.warning(f'Failed to parse Claude response for {condition_name}')
                return None
        else:
            logger.warning(f'Claude API error: {response.status_code}')
            return None
    except Exception as e:
        logger.warning(f'Claude restrictions error for {condition_name}: {e}')
        return None

def get_food_restrictions(condition_name, severity='unknown', confidence=0.5):
    """Get food restrictions for a health condition - try Ollama then Claude (with caching)"""
    # Try Ollama first
    restrictions = get_food_restrictions_from_ollama(condition_name, severity, confidence)
    if restrictions:
        return restrictions

    # Fall back to Claude
    restrictions = get_food_restrictions_from_claude(condition_name, severity, confidence)
    if restrictions:
        return restrictions

    # Fall back to hardcoded defaults if AI fails
    logger.warning(f'AI failed for {condition_name}, using defaults')
    return HEALTH_CONDITION_RESTRICTIONS_DEFAULT.get(condition_name.lower(), {'avoid': [], 'prefer': []})

HEALTH_CONDITION_RESTRICTIONS_DEFAULT = {
    'diabetes': {
        'avoid': ['pizza', 'sugary drinks', 'soda', 'candy', 'cookies', 'desserts', 'ice cream'],
        'prefer': ['salad', 'apple', 'carrot', 'spinach', 'broccoli', 'fish']
    },
    'hypertension': {
        'avoid': ['pizza', 'salt-heavy foods', 'cured meats', 'fried foods', 'salty snacks', 'processed foods'],
        'prefer': ['salad', 'banana', 'grilled chicken', 'fresh vegetables', 'fish']
    },
    'heart disease': {
        'avoid': ['fried foods', 'saturated fat', 'sugary drinks', 'candy', 'processed foods', 'salty foods', 'pizza'],
        'prefer': ['fish', 'vegetables', 'fruits', 'whole grains', 'olive oil']
    },
    'high blood pressure': {
        'avoid': ['pizza', 'salt-heavy foods', 'cured meats', 'fried foods', 'salty snacks', 'processed foods'],
        'prefer': ['salad', 'banana', 'grilled chicken', 'fresh vegetables', 'fish']
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
    if not food_items or not health_profile:
        return 'safe', 'No health profile to evaluate against'

    food_names = [item['name'].lower().strip() for item in food_items]
    conditions = [c.lower().strip() for c in health_profile.get('conditions', [])] if health_profile.get('conditions') else []
    allergens = [a.lower().strip() for a in health_profile.get('allergens', [])] if health_profile.get('allergens') else []

    # Early exit if no conditions or allergens
    if not conditions and not allergens:
        return 'safe', 'This food appears to be safe for your health profile'

    # Check for allergens in food names (substring matching)
    for allergen in allergens:
        # Extract base allergen name (e.g., "peanut allergy" -> "peanut")
        allergen_base = allergen.replace('allergy', '').replace('allergic', '').replace('allergies', '').replace('allergy to', '').strip()
        if not allergen_base or allergen_base == 'food':
            allergen_base = allergen

        # Check if allergen matches food (with some flexibility)
        for food in food_names:
            if allergen_base in food or food in allergen_base:
                return 'danger', f'⚠️ This food contains {allergen} which you are allergic to'

    # Check for restricted foods based on health conditions
    restricted_foods = []
    matched_conditions = []

    for condition in conditions:
        # Skip empty conditions
        if not condition:
            continue

        # Get food restrictions from AI (Ollama → Claude)
        restrictions = get_food_restrictions(condition)
        if restrictions:
            avoid_foods = restrictions.get('avoid', [])
            restricted_foods.extend(avoid_foods)
            matched_conditions.append(condition)
            logger.info(f"✓ Got restrictions from AI for condition '{condition}': {len(avoid_foods)} foods to avoid")
        else:
            logger.info(f"⚠️ Could not get restrictions for condition '{condition}'")

    # Check if any food is in restricted list
    for food in food_names:
        for restricted in restricted_foods:
            restricted_lower = restricted.lower().strip()
            if food == restricted_lower or restricted_lower in food or food in restricted_lower:
                conditions_str = ', '.join(matched_conditions) if matched_conditions else ', '.join(conditions)
                logger.info(f"🛑 Food '{food}' is restricted for {conditions_str}")
                return 'caution', f'This food is not recommended for your health profile ({conditions_str})'

    return 'safe', 'This food appears to be safe for your health profile'
