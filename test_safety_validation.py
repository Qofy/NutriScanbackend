#!/usr/bin/env python
"""
Safety Validation Testing for Recommendations
Tests: Allergy contraindications, Chronic disease contraindications
"""

import json
from typing import List, Dict

class SafetyValidator:
    """Validate recommendations against allergies and chronic diseases"""

    # Allergy-to-food contraindication map
    ALLERGY_CONTRAINDICATIONS = {
        'peanuts': ['peanut butter', 'peanut oil', 'trail mix', 'satay', 'peanut sauce'],
        'shellfish': ['shrimp', 'crab', 'lobster', 'oyster', 'clam', 'mussel'],
        'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'ice cream'],
        'gluten': ['wheat', 'bread', 'pasta', 'cereals', 'baked goods'],
        'tree nuts': ['almond', 'walnut', 'cashew', 'pecan', 'pistachio'],
        'fish': ['salmon', 'tuna', 'cod', 'trout', 'mackerel'],
        'eggs': ['egg noodles', 'mayonnaise', 'baked goods'],
        'soy': ['tofu', 'soy sauce', 'tempeh', 'edamame'],
    }

    # Chronic disease contraindication map
    DISEASE_CONTRAINDICATIONS = {
        'diabetes': {
            'foods': ['sugar', 'candy', 'soda', 'refined carbs', 'white rice', 'pastries', 'desserts'],
            'guidelines': 'Limit refined carbohydrates, monitor blood sugar, high fiber foods recommended'
        },
        'hypertension': {
            'foods': ['high sodium', 'salt', 'processed foods', 'cured meats', 'fast food'],
            'guidelines': 'Reduce sodium intake, limit caffeine, increase potassium-rich foods'
        },
        'heart disease': {
            'foods': ['saturated fat', 'trans fat', 'cholesterol-rich', 'fried foods', 'high sodium'],
            'guidelines': 'Reduce saturated fats, increase omega-3s, lean proteins'
        },
        'kidney disease': {
            'foods': ['high potassium', 'high phosphorus', 'high sodium', 'protein-heavy'],
            'guidelines': 'Restrict sodium, potassium, phosphorus; moderate protein'
        },
        'celiac': {
            'foods': ['gluten', 'wheat', 'barley', 'rye', 'oats (unless certified)'],
            'guidelines': 'Strict gluten-free diet required'
        },
        'prediabetes': {
            'foods': ['refined carbs', 'sugar', 'sugary drinks', 'processed foods'],
            'guidelines': 'Reduce refined carbs, increase fiber, monitor weight'
        },
    }

    @staticmethod
    def check_allergy_contraindications(food_items: List[str], allergies: List[str]) -> Dict:
        """Check if recommended foods conflict with known allergies"""

        warnings = []
        safe = True

        food_items_lower = [f.lower() for f in food_items]
        allergies_lower = [a.lower() for a in allergies]

        for allergy in allergies_lower:
            if allergy in SafetyValidator.ALLERGY_CONTRAINDICATIONS:
                contraindicated_foods = SafetyValidator.ALLERGY_CONTRAINDICATIONS[allergy]

                for food in food_items_lower:
                    for contraindicated in contraindicated_foods:
                        if contraindicated.lower() in food.lower() or food.lower() in contraindicated.lower():
                            warnings.append({
                                'type': 'ALLERGY_CONTRAINDICATION',
                                'severity': 'CRITICAL',
                                'message': f'⚠️ CRITICAL: {food.title()} may contain {allergy.title()} allergen',
                                'allergy': allergy,
                                'food': food,
                                'action': 'DO NOT RECOMMEND - User has documented allergy'
                            })
                            safe = False

        return {
            'safe': safe,
            'allergy_warnings': warnings,
            'total_warnings': len(warnings)
        }

    @staticmethod
    def check_disease_contraindications(food_items: List[str], conditions: List[str]) -> Dict:
        """Check if recommended foods conflict with chronic disease management"""

        warnings = []
        safe = True

        food_items_lower = [f.lower() for f in food_items]
        conditions_lower = [c.lower() for c in conditions]

        for condition in conditions_lower:
            # Find matching condition (partial match)
            matching_condition = None
            for disease_key in SafetyValidator.DISEASE_CONTRAINDICATIONS.keys():
                if disease_key in condition:
                    matching_condition = disease_key
                    break

            if matching_condition:
                contraindicated_foods = SafetyValidator.DISEASE_CONTRAINDICATIONS[matching_condition]['foods']
                guidelines = SafetyValidator.DISEASE_CONTRAINDICATIONS[matching_condition]['guidelines']

                for food in food_items_lower:
                    for contraindicated in contraindicated_foods:
                        if contraindicated.lower() in food.lower() or food.lower() in contraindicated.lower():
                            warnings.append({
                                'type': 'DISEASE_CONTRAINDICATION',
                                'severity': 'WARNING',
                                'message': f'⚠️ WARNING: {food.title()} conflicts with {matching_condition.title()} management',
                                'condition': matching_condition,
                                'food': food,
                                'guidelines': guidelines,
                                'action': 'CAUTION - Consider alternatives'
                            })
                            safe = False

        return {
            'safe': safe,
            'disease_warnings': warnings,
            'total_warnings': len(warnings)
        }

    @staticmethod
    def validate_recommendation(food_items: List[str], allergies: List[str], conditions: List[str]) -> Dict:
        """Complete safety validation for a recommendation"""

        allergy_check = SafetyValidator.check_allergy_contraindications(food_items, allergies)
        disease_check = SafetyValidator.check_disease_contraindications(food_items, conditions)

        all_safe = allergy_check['safe'] and disease_check['safe']
        all_warnings = allergy_check['allergy_warnings'] + disease_check['disease_warnings']

        return {
            'overall_safe': all_safe,
            'total_warnings': len(all_warnings),
            'warnings': all_warnings,
            'allergy_check': allergy_check,
            'disease_check': disease_check,
            'recommendation_status': 'APPROVED' if all_safe else 'FLAGGED FOR REVIEW'
        }


def run_safety_tests():
    """Run comprehensive safety validation tests"""

    print("\n" + "="*100)
    print("🛡️  SAFETY VALIDATION TESTING - Allergy & Disease Contraindications")
    print("="*100)

    test_cases = [
        {
            'name': 'Peanut Allergy + Peanut-containing Food',
            'foods': ['peanut butter', 'banana'],
            'allergies': ['peanuts'],
            'conditions': [],
            'expected_warnings': 1,
            'severity': 'CRITICAL'
        },
        {
            'name': 'Shellfish Allergy + Seafood Restaurant',
            'foods': ['grilled shrimp', 'salad', 'rice'],
            'allergies': ['shellfish'],
            'conditions': [],
            'expected_warnings': 1,
            'severity': 'CRITICAL'
        },
        {
            'name': 'Diabetes + High Sugar Food',
            'foods': ['soda', 'candy', 'apple'],
            'allergies': [],
            'conditions': ['diabetes'],
            'expected_warnings': 2,
            'severity': 'WARNING'
        },
        {
            'name': 'Hypertension + High Sodium Food',
            'foods': ['processed salad', 'canned soup', 'bacon'],
            'allergies': [],
            'conditions': ['hypertension'],
            'expected_warnings': 2,
            'severity': 'WARNING'
        },
        {
            'name': 'Heart Disease + Saturated Fat',
            'foods': ['fried chicken', 'butter', 'whole milk'],
            'allergies': [],
            'conditions': ['coronary artery disease'],
            'expected_warnings': 3,
            'severity': 'WARNING'
        },
        {
            'name': 'Safe Recommendation (No Conflicts)',
            'foods': ['grilled chicken', 'steamed broccoli', 'brown rice'],
            'allergies': ['peanuts'],
            'conditions': ['diabetes', 'hypertension'],
            'expected_warnings': 0,
            'severity': 'SAFE'
        },
        {
            'name': 'Multiple Allergies + Multiple Diseases',
            'foods': ['shellfish', 'candy', 'bread', 'apple'],
            'allergies': ['shellfish', 'gluten'],
            'conditions': ['diabetes', 'heart disease'],
            'expected_warnings': 4,
            'severity': 'CRITICAL'
        },
    ]

    results = []
    passed = 0
    failed = 0

    for idx, test in enumerate(test_cases, 1):
        print(f"\n[Test {idx}/7] {test['name']}")
        print("-" * 100)

        result = SafetyValidator.validate_recommendation(
            test['foods'],
            test['allergies'],
            test['conditions']
        )

        print(f"Foods: {', '.join(test['foods'])}")
        print(f"Allergies: {', '.join(test['allergies']) if test['allergies'] else 'None'}")
        print(f"Conditions: {', '.join(test['conditions']) if test['conditions'] else 'None'}")
        print(f"\nResult: {result['recommendation_status']}")
        print(f"Warnings Found: {result['total_warnings']}")

        if result['warnings']:
            for warning in result['warnings']:
                severity_emoji = "🔴" if warning['severity'] == 'CRITICAL' else "🟡"
                print(f"  {severity_emoji} [{warning['severity']}] {warning['message']}")
        else:
            print(f"  ✅ No safety concerns")

        # Check test result
        test_passed = result['total_warnings'] == test['expected_warnings']
        if test_passed:
            passed += 1
            print(f"✅ PASS (Expected {test['expected_warnings']} warnings, got {result['total_warnings']})")
        else:
            failed += 1
            print(f"❌ FAIL (Expected {test['expected_warnings']} warnings, got {result['total_warnings']})")

        results.append({
            'test': test['name'],
            'passed': test_passed,
            'expected': test['expected_warnings'],
            'actual': result['total_warnings'],
            'result': result
        })

    # Summary
    print(f"\n{'='*100}")
    print(f"📊 SAFETY VALIDATION TEST SUMMARY")
    print(f"{'='*100}")
    print(f"\nTotal Tests: {len(test_cases)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_cases))*100:.1f}%")

    print(f"\n{'='*100}")
    print(f"🛡️  SAFETY VALIDATION: {'READY FOR PRODUCTION' if failed == 0 else 'NEEDS FIXES'}")
    print(f"{'='*100}\n")

    return {
        'total_tests': len(test_cases),
        'passed': passed,
        'failed': failed,
        'results': results
    }


if __name__ == '__main__':
    run_safety_tests()
