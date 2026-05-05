FOOD_DATABASE = {
    'apple': {
        'calories': 95,
        'protein': 0.5,
        'carbs': 25,
        'fat': 0.3,
        'fiber': 4.4,
        'vitamins': {'C': '8.4mg', 'A': '54IU'},
        'minerals': {'potassium': '195mg'},
        'allergens': []
    },
    'carrot': {
        'calories': 41,
        'protein': 0.9,
        'carbs': 10,
        'fat': 0.2,
        'fiber': 2.8,
        'vitamins': {'A': '961mcg', 'C': '3.6mg'},
        'minerals': {'potassium': '320mg'},
        'allergens': []
    },
    'salad': {
        'calories': 15,
        'protein': 1.2,
        'carbs': 3,
        'fat': 0.2,
        'fiber': 1.2,
        'vitamins': {'K': '145mcg', 'A': '4623IU'},
        'minerals': {'iron': '0.8mg'},
        'allergens': []
    },
    'grilled chicken': {
        'calories': 165,
        'protein': 31,
        'carbs': 0,
        'fat': 3.6,
        'fiber': 0,
        'vitamins': {'B12': '0.31mcg', 'B6': '0.88mg'},
        'minerals': {'selenium': '27mcg'},
        'allergens': []
    },
    'rice': {
        'calories': 130,
        'protein': 2.7,
        'carbs': 28,
        'fat': 0.3,
        'fiber': 0.4,
        'vitamins': {'B1': '0.07mg'},
        'minerals': {'manganese': '0.76mg'},
        'allergens': []
    },
    'pizza': {
        'calories': 285,
        'protein': 12,
        'carbs': 36,
        'fat': 10,
        'fiber': 1.8,
        'vitamins': {'C': '1.5mg'},
        'minerals': {'calcium': '200mg', 'sodium': '600mg'},
        'allergens': ['gluten', 'dairy']
    },
    'peanuts': {
        'calories': 567,
        'protein': 25.8,
        'carbs': 16.1,
        'fat': 49.2,
        'fiber': 8.6,
        'vitamins': {'E': '8.3mg'},
        'minerals': {'magnesium': '168mg'},
        'allergens': ['peanuts']
    },
}

HEALTH_CONDITION_RESTRICTIONS = {
    'diabetes': {
        'avoid': ['pizza', 'sugary drinks'],
        'prefer': ['salad', 'apple', 'carrot']
    },
    'hypertension': {
        'avoid': ['pizza', 'salt-heavy foods'],
        'prefer': ['salad', 'banana', 'grilled chicken']
    },
    'allergies': {
        'peanut_allergy': {
            'avoid': ['peanuts'],
            'safe': ['apple', 'carrot', 'salad']
        }
    }
}

def get_nutritional_info(food_items):
    nutrition_data = {}
    for item in food_items:
        food_name = item['name'].lower()
        if food_name in FOOD_DATABASE:
            nutrition_data[food_name] = FOOD_DATABASE[food_name]
        else:
            nutrition_data[food_name] = {
                'status': 'not_found',
                'message': f'Nutritional data for {item["name"]} not in database'
            }
    return nutrition_data

def evaluate_safety(food_items, health_profile):
    food_names = [item['name'].lower() for item in food_items]
    conditions = health_profile.get('conditions', [])
    allergens = health_profile.get('allergens', [])

    restricted_foods = []
    for condition in conditions:
        if condition.lower() in HEALTH_CONDITION_RESTRICTIONS:
            restricted = HEALTH_CONDITION_RESTRICTIONS[condition.lower()].get('avoid', [])
            restricted_foods.extend(restricted)

    for food in food_names:
        if food in restricted_foods:
            return 'caution', f'This food may not be suitable for {", ".join(conditions)}'

    for allergen in allergens:
        for food in food_names:
            if allergen.lower() in FOOD_DATABASE.get(food, {}).get('allergens', []):
                return 'danger', f'This food contains {allergen} which you are allergic to'

    return 'safe', 'This food appears to be safe for your health profile'
