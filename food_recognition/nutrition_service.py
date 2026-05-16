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

def evaluate_food_safety_with_ollama(food_items, health_conditions, extracted_medical_data=None):
    """Use Ollama to intelligently evaluate if foods are safe for user's specific health conditions"""
    try:
        api_key = getattr(settings, 'OLLAMA_API_KEY', None)
        if not api_key or not api_key.strip():
            logger.info('❌ Ollama API key not configured for food safety')
            return None

        food_names = [item['name'] for item in food_items]
        conditions_str = ', '.join(health_conditions) if health_conditions else 'No specific conditions'

        # Include extracted medical data in prompt if available
        medical_context = ""
        if extracted_medical_data:
            if extracted_medical_data.get('extracted_summary'):
                medical_context = f"\nExtracted Medical Report:\n{extracted_medical_data['extracted_summary'][:500]}"
            elif extracted_medical_data.get('raw_text_preview'):
                medical_context = f"\nMedical Report Preview:\n{extracted_medical_data['raw_text_preview'][:300]}"

        prompt = f"""You are a nutritionist evaluating food safety. A patient with the following health conditions wants to eat these foods:

Health Conditions: {conditions_str}
{medical_context}

Foods to evaluate: {', '.join(food_names)}

For each food, determine if it is:
- SAFE: Good for this health condition
- CAUTION: May need to be limited or monitored
- DANGER: Should be avoided

Return ONLY a JSON object (no markdown, no other text) with this exact structure:
{{
    "overall_safety": "safe|caution|danger",
    "recommendations": [
        {{"food": "food_name", "safety": "safe|caution|danger", "reason": "brief explanation"}}
    ],
    "summary": "brief overall assessment"
}}

Be specific and considerate of the patient's actual medical situation."""

        logger.info(f'🧠 Using Ollama to evaluate food safety for conditions: {conditions_str}')

        url = 'https://ollama.com/api/chat'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': 'ministral-3:8b',
            'messages': [{'role': 'user', 'content': prompt}],
            'stream': False,
            'temperature': 0.3
        }

        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            content = data.get('message', {}).get('content', '').strip()
            try:
                result = json.loads(content)
                logger.info(f'✅ Ollama food safety evaluation: {result.get("overall_safety")}')
                return result
            except json.JSONDecodeError:
                logger.warning('Failed to parse Ollama food safety response')
                return None
        else:
            logger.warning(f'Ollama API error for food safety: {response.status_code}')
            return None
    except Exception as e:
        logger.warning(f'Ollama food safety evaluation failed: {e}')
        return None


def evaluate_safety(food_items, health_profile, extracted_medical_data=None):
    """
    Evaluate food safety using Ollama AI with priority:
    1. PRIMARY: Medical Report extracted data (if available)
    2. SECONDARY: User health profile (conditions/allergens)
    3. FALLBACK: Safe (no health data available)
    """
    if not food_items:
        return 'safe', 'No food items to evaluate'

    # PRIORITY 1: Use extracted medical data if available (PRIMARY source)
    if extracted_medical_data:
        logger.info('🏥 PRIMARY SOURCE: Using extracted medical report data for safety evaluation')
        medical_conditions = extracted_medical_data.get('conditions', [])
        medical_allergens = extracted_medical_data.get('allergens', [])

        # Extract condition names from medical data structure
        conditions = []
        for item in medical_conditions:
            if isinstance(item, dict):
                conditions.append(item.get('condition', ''))
            else:
                conditions.append(str(item))
        conditions = [c.lower().strip() for c in conditions if c]

        allergens = []
        for item in medical_allergens:
            if isinstance(item, dict):
                allergens.append(item.get('allergen', ''))
            else:
                allergens.append(str(item))
        allergens = [a.lower().strip() for a in allergens if a]

        if conditions or allergens:
            ollama_result = evaluate_food_safety_with_ollama(food_items, conditions + allergens, extracted_medical_data)
            if ollama_result:
                overall = ollama_result.get('overall_safety', 'safe')
                summary = ollama_result.get('summary', '')
                logger.info(f'✅ MEDICAL REPORT evaluation via Ollama: {overall}')
                return overall, summary

    # PRIORITY 2: Fall back to user health profile (SECONDARY source)
    if health_profile:
        conditions = [c.lower().strip() for c in health_profile.get('conditions', [])] if health_profile.get('conditions') else []
        allergens = [a.lower().strip() for a in health_profile.get('allergens', [])] if health_profile.get('allergens') else []

        if conditions or allergens:
            logger.info('👤 SECONDARY SOURCE: Using user health profile for safety evaluation')
            ollama_result = evaluate_food_safety_with_ollama(food_items, conditions + allergens, None)
            if ollama_result:
                overall = ollama_result.get('overall_safety', 'safe')
                summary = ollama_result.get('summary', '')
                logger.info(f'✅ USER PROFILE evaluation via Ollama: {overall}')
                return overall, summary

    # PRIORITY 3: No health data available - return safe
    logger.info('⚠️ No medical report or user profile data available - defaulting to safe')
    return 'safe', 'No health profile or medical data available - food appears generally safe'
