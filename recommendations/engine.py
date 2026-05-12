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
    def generate_ai_recommendations(health_profile, food_history):
        """
        Generate personalized recommendations using AI (Ollama Cloud → Claude AI fallback)
        health_profile: {conditions: [], allergens: [], dietary_restrictions: []}
        food_history: {recent_foods: [], nutritional_patterns: {}}
        """
        import json
        import requests
        from django.conf import settings
        import logging

        logger = logging.getLogger(__name__)

        # Build the prompt
        conditions_str = ', '.join(health_profile.get('conditions', [])) or 'None'
        allergens_str = ', '.join(health_profile.get('allergens', [])) or 'None'
        restrictions_str = ', '.join(health_profile.get('dietary_restrictions', [])) or 'None'

        recent_foods = ', '.join([f.get('name', 'Unknown') for f in food_history.get('recent_foods', [])]) or 'No recent scans'

        # Build list of conditions for the AI to reference
        user_conditions_list = health_profile.get('conditions', [])
        conditions_list_str = ', '.join(user_conditions_list) if user_conditions_list else 'No specific conditions'

        prompt = f"""You are a personalized nutrition advisor. Based on the user's health profile and eating history, generate 5 specific, actionable food recommendations.

USER HEALTH PROFILE:
- Health Conditions: {conditions_str}
- Allergens: {allergens_str}
- Dietary Restrictions: {restrictions_str}

RECENT FOODS EATEN:
{recent_foods}

Return ONLY a valid JSON array with exactly 5 recommendation objects. Each object must have:
{{
  "food_item": "food name",
  "emoji": "single emoji",
  "description": "why this food is good (1-2 sentences)",
  "condition": "which health condition this addresses: {conditions_list_str}",
  "benefit": "specific health benefit (1 sentence)",
  "severity": "safe" (only safe foods),
  "nutritional_info": {{"calories": number, "protein": number, "carbs": number, "fiber": number}}
}}

IMPORTANT: The "condition" field MUST be one of the user's actual health conditions: {conditions_list_str}
Do NOT use "general" - use the specific condition this food benefits.
Be specific and personalized. Focus on foods that address their conditions and avoid allergens."""

        # Try Ollama Cloud first
        try:
            ollama_key = getattr(settings, 'OLLAMA_API_KEY', None)
            if ollama_key and ollama_key.strip():
                logger.info("🔍 Trying Ollama Cloud for recommendations...")

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
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('message', {}).get('content', '').strip()

                    # Clean up markdown if needed
                    if response_text.startswith('```'):
                        response_text = response_text.split('```')[1]
                        if response_text.startswith('json'):
                            response_text = response_text[4:]

                    recs = json.loads(response_text)
                    logger.info("✅ Generated recommendations via Ollama Cloud")
                    return recs
                else:
                    logger.warning(f"Ollama Cloud returned {response.status_code}, trying Claude AI...")
        except Exception as e:
            logger.warning(f"Ollama Cloud failed: {str(e)}, trying Claude AI...")

        # Fallback to Claude AI
        try:
            from anthropic import Anthropic

            logger.info("🔍 Trying Claude AI for recommendations...")
            client = Anthropic()

            response = client.messages.create(
                model="claude-opus-4-1",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()

            # Clean up markdown if needed
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]

            recs = json.loads(response_text)
            logger.info("✅ Generated recommendations via Claude AI")
            return recs
        except Exception as e:
            logger.error(f"Claude AI failed: {str(e)}")
            raise Exception(f"Failed to generate recommendations: {str(e)}")
