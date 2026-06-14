#!/usr/bin/env python
"""
Baseline extraction methods for NLP evaluation:
1. Keyword-only (regex matching)
2. LLM-only (Claude without system processing)
3. System extraction (current approach)
"""

import re
import json
from pathlib import Path

# Keyword dictionary for baseline extraction
CONDITION_KEYWORDS = {
    'HIV': ['HIV', 'human immunodeficiency virus'],
    'AIDS': ['AIDS', 'acquired immunodeficiency'],
    'Prediabetes': ['prediabetes', 'elevated blood sugar', 'hba1c', 'glucose'],
    'Type 2 Diabetes': ['type 2 diabetes', 'diabetes mellitus', 'diabetic'],
    'Hypertension': ['hypertension', 'high blood pressure', 'stage 1', 'stage 2'],
    'Coronary Artery Disease': ['coronary artery disease', 'cad', 'coronary'],
    'Myocardial Ischemia': ['myocardial ischemia', 'ischemia', 'ischemic'],
    'Heart Failure': ['heart failure', 'ventricular dysfunction', 'ejection fraction'],
    'Syphilis': ['syphilis', 'treponema pallidum'],
    'Hepatitis': ['hepatitis', 'liver disease'],
}

ALLERGEN_KEYWORDS = {
    'Peanuts': ['peanut', 'groundnut'],
    'Shellfish': ['shellfish', 'shrimp', 'crab', 'lobster'],
    'Dairy': ['dairy', 'milk', 'lactose', 'cheese'],
    'Gluten': ['gluten', 'wheat', 'celiac'],
    'Tree Nuts': ['tree nut', 'almond', 'walnut', 'cashew'],
    'Fish': ['fish', 'salmon', 'cod'],
}

MEDICATION_KEYWORDS = {
    'Penicillin': ['penicillin', 'amoxicillin'],
    'Lisinopril': ['lisinopril', 'ace inhibitor'],
    'Metformin': ['metformin', 'glucophage'],
    'Aspirin': ['aspirin', 'acetylsalicylic acid'],
    'Statin': ['atorvastatin', 'simvastatin', 'statin'],
}

RESTRICTION_KEYWORDS = {
    'Limit Sodium': ['sodium', 'salt', 'high sodium'],
    'Limit Sugar': ['sugar', 'glucose', 'carbohydrate', 'refined carb'],
    'Limit Fat': ['saturated fat', 'trans fat', 'cholesterol'],
    'Limit Caffeine': ['caffeine', 'coffee', 'tea'],
}


class BaselineExtractor:
    """Keyword-only extraction baseline"""

    @staticmethod
    def extract_conditions(text):
        """Extract conditions using keyword matching"""
        conditions = []
        text_lower = text.lower()

        for condition, keywords in CONDITION_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    conditions.append({
                        'condition': condition,
                        'method': 'keyword_match',
                        'keyword_found': keyword,
                        'confidence': 0.7
                    })
                    break

        return conditions

    @staticmethod
    def extract_allergens(text):
        """Extract allergens using keyword matching"""
        allergens = []
        text_lower = text.lower()

        allergy_indicators = ['allerg', 'reaction', 'avoid', 'sensitivity', 'intolerance']

        for allergen, keywords in ALLERGEN_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # Check if in allergy context
                    if any(indicator in text_lower for indicator in allergy_indicators):
                        allergens.append({
                            'allergen': allergen,
                            'method': 'keyword_match',
                            'keyword_found': keyword,
                            'confidence': 0.65
                        })
                        break

        return allergens

    @staticmethod
    def extract_medications(text):
        """Extract medications using keyword matching"""
        medications = []
        text_lower = text.lower()

        for medication, keywords in MEDICATION_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    medications.append({
                        'medication': medication,
                        'method': 'keyword_match',
                        'keyword_found': keyword,
                        'confidence': 0.6
                    })
                    break

        return medications

    @staticmethod
    def extract_restrictions(text):
        """Extract dietary restrictions using keyword matching"""
        restrictions = []
        text_lower = text.lower()

        for restriction, keywords in RESTRICTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    restrictions.append({
                        'restriction': restriction,
                        'method': 'keyword_match',
                        'keyword_found': keyword,
                        'confidence': 0.6
                    })
                    break

        return restrictions

    @staticmethod
    def extract_from_text(text):
        """Complete keyword-based extraction"""
        return {
            'conditions': BaselineExtractor.extract_conditions(text),
            'allergens': BaselineExtractor.extract_allergens(text),
            'medications': BaselineExtractor.extract_medications(text),
            'dietary_restrictions': BaselineExtractor.extract_restrictions(text),
            'method': 'keyword_only'
        }


class LLMOnlyExtractor:
    """LLM extraction without system processing (placeholder)"""

    @staticmethod
    def extract_from_text(text):
        """
        Extract using Claude API directly without system processing.
        This is a placeholder - actual implementation would call Claude API.
        """
        return {
            'conditions': [],
            'allergens': [],
            'medications': [],
            'dietary_restrictions': [],
            'method': 'llm_only',
            'note': 'Requires Claude API call - implement separately'
        }


if __name__ == '__main__':
    # Test on sample text
    sample_text = """
    Patient: John Doe
    Diagnosis: HIV/AIDS, Type 2 Diabetes
    Allergies: Peanuts, Shellfish
    Medications: Penicillin, Metformin
    Dietary Restrictions: Limit sodium, reduce sugar intake
    """

    print("\n📊 BASELINE EXTRACTION TEST")
    print("="*60)
    print(f"Sample Text: {sample_text[:100]}...")

    result = BaselineExtractor.extract_from_text(sample_text)

    print(f"\n✅ Conditions Found: {len(result['conditions'])}")
    for c in result['conditions']:
        print(f"   • {c['condition']} (keyword: {c['keyword_found']})")

    print(f"\n✅ Allergens Found: {len(result['allergens'])}")
    for a in result['allergens']:
        print(f"   • {a['allergen']} (keyword: {a['keyword_found']})")

    print(f"\n✅ Medications Found: {len(result['medications'])}")
    for m in result['medications']:
        print(f"   • {m['medication']} (keyword: {m['keyword_found']})")

    print(f"\n✅ Restrictions Found: {len(result['dietary_restrictions'])}")
    for r in result['dietary_restrictions']:
        print(f"   • {r['restriction']} (keyword: {r['keyword_found']})")

    print("\n" + "="*60)
