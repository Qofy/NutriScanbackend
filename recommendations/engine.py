# RECOMMENDATION_DATABASE = [
#     {
#         'food_item': 'Carrots',
#         'emoji': '🥕',
#         'description': 'Rich in beta-carotene and vitamin A. Excellent for eye health and immune function.',
#         'conditions': ['diabetes', 'heart_disease'],
#         'benefit': 'Low glycemic index helps maintain stable blood sugar levels',
#         'severity': 'safe',
#         'nutrition': {
#             'calories': 41,
#             'protein': 0.9,
#             'carbs': 10,
#             'fiber': 2.8,
#         }
#     },
#     {
#         'food_item': 'Spinach',
#         'emoji': '🥬',
#         'description': 'Nutrient-dense leafy green with excellent mineral content and low calories.',
#         'conditions': ['hypertension', 'diabetes', 'heart_disease'],
#         'benefit': 'High in potassium which helps regulate blood pressure',
#         'severity': 'safe',
#         'nutrition': {
#             'calories': 23,
#             'protein': 2.7,
#             'carbs': 3.6,
#             'fiber': 2.2,
#         }
#     },
#     {
#         'food_item': 'Blueberries',
#         'emoji': '🫐',
#         'description': 'Packed with antioxidants and polyphenols for cardiovascular health.',
#         'conditions': ['hypertension', 'heart_disease'],
#         'benefit': 'Anthocyanins help improve blood vessel function',
#         'severity': 'safe',
#         'nutrition': {
#             'calories': 57,
#             'protein': 0.7,
#             'carbs': 14.5,
#             'fiber': 2.4,
#         }
#     },
#     {
#         'food_item': 'Salmon',
#         'emoji': '🐟',
#         'description': 'Rich in omega-3 fatty acids that support heart and brain health.',
#         'conditions': ['heart_disease', 'hypertension'],
#         'benefit': 'Reduces inflammation and supports healthy cholesterol levels',
#         'severity': 'safe',
#         'nutrition': {
#             'calories': 208,
#             'protein': 20,
#             'carbs': 0,
#             'fat': 13,
#         }
#     },
#     {
#         'food_item': 'Apples',
#         'emoji': '🍎',
#         'description': 'Excellent source of fiber and vitamin C with natural sweetness.',
#         'conditions': ['diabetes', 'heart_disease'],
#         'benefit': 'Soluble fiber helps regulate blood sugar and cholesterol',
#         'severity': 'safe',
#         'nutrition': {
#             'calories': 95,
#             'protein': 0.5,
#             'carbs': 25,
#             'fiber': 4.4,
#         }
#     },
#     {
#         'food_item': 'Broccoli',
#         'emoji': '🥦',
#         'description': 'Cruciferous vegetable rich in vitamins C, K, and fiber.',
#         'conditions': ['diabetes', 'heart_disease', 'hypertension'],
#         'benefit': 'Supports cardiovascular and metabolic health',
#         'severity': 'safe',
#         'nutrition': {
#             'calories': 34,
#             'protein': 2.8,
#             'carbs': 7,
#             'fiber': 2.4,
#         }
#     },
#     {
#         'food_item': 'Bananas',
#         'emoji': '🍌',
#         'description': 'Natural source of potassium and B vitamins for energy.',
#         'conditions': ['hypertension', 'heart_disease'],
#         'benefit': 'High potassium content helps regulate blood pressure naturally',
#         'severity': 'safe',
#         'nutrition': {
#             'calories': 89,
#             'protein': 1.1,
#             'carbs': 23,
#             'fiber': 2.6,
#         }
#     },
#     {
#         'food_item': 'Almonds',
#         'emoji': '🌰',
#         'description': 'Tree nuts packed with healthy unsaturated fats and protein.',
#         'conditions': ['heart_disease', 'cholesterol'],
#         'benefit': 'May help lower cholesterol and reduce heart disease risk',
#         'severity': 'safe',
#         'nutrition': {
#             'calories': 579,
#             'protein': 21.2,
#             'carbs': 21.6,
#             'fat': 49.9,
#         },
#         'allergens': ['tree_nuts']
#     },
#     {
#         'food_item': 'Peanuts',
#         'emoji': '🥜',
#         'description': 'Good protein source with healthy fats, but caution for allergy sufferers.',
#         'conditions': [],
#         'benefit': 'Contains aflatoxins - avoid if you have peanut allergies',
#         'severity': 'danger',
#         'nutrition': {
#             'calories': 567,
#             'protein': 25.8,
#             'carbs': 16.1,
#             'fat': 49.2,
#         },
#         'allergens': ['peanuts']
#     },
#     {
#         'food_item': 'Pizza',
#         'emoji': '🍕',
#         'description': 'High sodium and saturated fat content, not ideal for certain conditions.',
#         'conditions': [],
#         'benefit': 'Occasional consumption only - high sodium affects blood pressure',
#         'severity': 'caution',
#         'nutrition': {
#             'calories': 285,
#             'protein': 12,
#             'carbs': 36,
#             'fat': 10,
#         },
#         'avoid_for_conditions': ['hypertension', 'diabetes', 'heart_disease']
#     },
# ]

class RecommendationEngine:
    @staticmethod
    def generate_recommendations(user_profile):
        user_conditions = user_profile.get('conditions', [])
        user_allergens = user_profile.get('allergens', [])

        recommendations = []

        for food in RECOMMENDATION_DATABASE:
            skip = False

            for allergen in user_allergens:
                if allergen.lower() in [a.lower() for a in food.get('allergens', [])]:
                    skip = True
                    break

            if skip:
                continue

            if user_conditions:
                food_conditions = [c.lower() for c in food.get('conditions', [])]
                avoid_for_conditions = [c.lower() for c in food.get('avoid_for_conditions', [])]
                user_conditions_lower = [c.lower() for c in user_conditions]

                has_match = any(cond in food_conditions for cond in user_conditions_lower)
                should_avoid = any(cond in avoid_for_conditions for cond in user_conditions_lower)

                if should_avoid:
                    continue

                if has_match or not food.get('conditions'):
                    recommendations.append(food)
            else:
                recommendations.append(food)

        return sorted(recommendations, key=lambda x: x.get('severity') == 'safe', reverse=True)

    @staticmethod
    def get_personalized_tips(user_profile):
        conditions = user_profile.get('conditions', [])
        tips = []

        if not conditions:
            tips.append({
                'title': 'Balanced Diet',
                'description': 'Include a variety of foods from all food groups for optimal nutrition'
            })
            return tips

        if any(c.lower() == 'diabetes' for c in conditions):
            tips.append({
                'title': 'Blood Sugar Management',
                'description': 'Monitor carbohydrate intake and pair carbs with protein and fiber'
            })
            tips.append({
                'title': 'Meal Timing',
                'description': 'Eat regular meals at consistent times to maintain stable blood sugar'
            })

        if any(c.lower() == 'hypertension' for c in conditions):
            tips.append({
                'title': 'Sodium Control',
                'description': 'Limit salt intake to less than 2300mg per day'
            })
            tips.append({
                'title': 'Potassium Rich Foods',
                'description': 'Include more fruits and vegetables high in potassium'
            })

        if any(c.lower() == 'heart_disease' for c in conditions):
            tips.append({
                'title': 'Heart Healthy Fats',
                'description': 'Choose unsaturated fats like olive oil and omega-3 rich fish'
            })
            tips.append({
                'title': 'Cholesterol Management',
                'description': 'Limit saturated fats and increase soluble fiber intake'
            })

        return tips

    @staticmethod
    def generate_ai_recommendations(health_profile, food_history, extracted_medical_data=None, user_country=None):
        """
        Generate personalized recommendations using AI (Ollama Cloud → Claude AI fallback)

        PRIORITY:
        1. extracted_medical_data (from medical report) - PRIMARY
        2. food_history (from food scans) - SECONDARY
        3. health_profile - fallback
        4. user_country - for regional food suggestions

        health_profile: {conditions: [], allergens: [], dietary_restrictions: []}
        food_history: {recent_foods: [], nutritional_patterns: {}}
        extracted_medical_data: {extracted_summary: str, raw_text_preview: str, ...}
        user_country: str (e.g., "Kenya", "Nigeria", "India")
        """
        import json
        import requests
        from django.conf import settings
        import logging

        logger = logging.getLogger(__name__)

        # Build the prompt with medical data as PRIMARY source
        conditions_str = ', '.join(health_profile.get('conditions', [])) or 'None'
        allergens_str = ', '.join(health_profile.get('allergens', [])) or 'None'
        restrictions_str = ', '.join(health_profile.get('dietary_restrictions', [])) or 'None'

        recent_foods = ', '.join([f.get('name', 'Unknown') for f in food_history.get('recent_foods', [])]) or 'No recent scans'

        # Build list of conditions for the AI to reference
        user_conditions_list = health_profile.get('conditions', [])
        conditions_list_str = ', '.join(user_conditions_list) if user_conditions_list else 'No specific conditions'

        # Add medical report context if available (PRIMARY source)
        medical_report_context = ""
        if extracted_medical_data:
            if extracted_medical_data.get('extracted_summary'):
                medical_report_context = f"""
MEDICAL REPORT (PRIMARY SOURCE - Extracted from actual medical document):
{extracted_medical_data['extracted_summary'][:800]}"""
            elif extracted_medical_data.get('raw_text_preview'):
                medical_report_context = f"""
MEDICAL REPORT (PRIMARY SOURCE - Extracted from actual medical document):
{extracted_medical_data['raw_text_preview'][:800]}"""

        # Build country context if available
        country_context = ""
        if user_country and user_country.strip():
            country_context = f"""

=== USER LOCATION ===
- Country: {user_country}
- Generate 3 recommendations from {user_country}'s local/traditional cuisine
- Generate 3 recommendations from continental/international cuisines"""
        else:
            country_context = """

=== RECOMMENDATION SPLIT ===
- Generate 3 recommendations from diverse global cuisines
- Generate 3 recommendations from common international foods"""

        # Adjust instruction based on whether country is provided
        recommendations_count = 6
        country_instruction = f"""
3. Generate {recommendations_count} specific, actionable food recommendations split as follows:
   - FIRST 3: {f'Local cuisine/traditional foods from {user_country}' if user_country else 'Diverse global cuisines'}
   - NEXT 3: {'Continental/international cuisines' if user_country else 'Common international foods'}
   - ALL recommendations must:
     * Address their actual medical conditions from the report
     * Avoid their documented allergens
     * Support their dietary restrictions
     * Consider their recent eating habits"""

        prompt = f"""You are a personalized nutrition advisor. Based on the user's MEDICAL REPORT (primary), eating history (secondary), and location (tertiary), generate {recommendations_count} specific, actionable food recommendations.

=== PRIMARY SOURCE: MEDICAL REPORT DATA ===
{medical_report_context}

=== SECONDARY SOURCE: RECENT FOOD SCANS ===
Recently eaten foods: {recent_foods}

=== USER HEALTH PROFILE ===
- Health Conditions: {conditions_str}
- Allergens: {allergens_str}
- Dietary Restrictions: {restrictions_str}{country_context}

INSTRUCTIONS:
1. PRIORITIZE recommendations based on the user's ACTUAL MEDICAL REPORT data
2. SECONDARY: Consider their recent food eating patterns to provide relevant advice{country_instruction}

Return ONLY a valid JSON array with exactly {recommendations_count} recommendation objects. Each object must have:
{{
  "food_item": "food name",
  "emoji": "single emoji",
  "description": "why this food is good (1-2 sentences)",
  "condition": "which health condition this addresses: {conditions_list_str}",
  "benefit": "specific health benefit (1 sentence)",
  "severity": "safe" (only safe foods),
  "nutritional_info": {{"calories": number, "protein": number, "carbs": number, "fiber": number}}
}}

IMPORTANT: The "condition" field MUST be one of the user's actual health conditions from their medical report: {conditions_list_str}
Do NOT use "general" - use the specific condition this food benefits.
Be specific and personalized based on their ACTUAL MEDICAL DATA, not generic recommendations.
Ensure the FIRST 3 recommendations are {f'from {user_country}' if user_country else 'from diverse regions'} and the NEXT 3 are from continental/international cuisines."""

        # Try Ollama Cloud for recommendations (prioritized)
        try:
            ollama_key = getattr(settings, 'OLLAMA_API_KEY', None)
            if ollama_key and ollama_key.strip():
                logger.info("🔍 Using Ollama Cloud for recommendations (nutritional info, safety, cautions)...")

                response = requests.post(
                    'https://ollama.com/api/chat',
                    headers={
                        'Authorization': f'Bearer {ollama_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'ministral-3:8b',
                        'messages': [{'role': 'user', 'content': prompt}],
                        'stream': False,
                        'temperature': 0.5
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('message', {}).get('content', '').strip()
                    logger.info(f"📊 Ollama response received: {len(response_text)} chars")

                    # Clean up markdown if needed
                    if response_text.startswith('```'):
                        response_text = response_text.split('```')[1]
                        if response_text.startswith('json'):
                            response_text = response_text[4:]

                    recs = json.loads(response_text)
                    logger.info("✅ Generated recommendations via Ollama Cloud (with nutritional info & safety)")
                    return recs
                else:
                    logger.error(f"Ollama API returned {response.status_code}: {response.text}")
                    raise Exception(f"Ollama API error: {response.status_code}")
            else:
                logger.warning("⚠️ OLLAMA_API_KEY not configured")
                raise Exception("Ollama API key not configured")
        except Exception as e:
            logger.error(f"Ollama Cloud failed: {str(e)}")

        # Ollama is required - no fallback
        logger.error("❌ Recommendations require Ollama API key to be configured")
        raise Exception("Failed to generate recommendations: OLLAMA_API_KEY not configured. Please set OLLAMA_API_KEY in environment variables.")
