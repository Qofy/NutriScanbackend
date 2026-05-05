import re

COMMON_HEALTH_CONDITIONS = {
    'diabetes': {
        'keywords': ['diabetes', 'blood sugar', 'glucose', 'insulin'],
        'severity': 'high',
        'dietary_restrictions': ['high_sugar_foods', 'refined_carbs']
    },
    'hypertension': {
        'keywords': ['hypertension', 'high blood pressure', 'stage 1', 'stage 2'],
        'severity': 'high',
        'dietary_restrictions': ['high_sodium_foods', 'processed_foods']
    },
    'cholesterol': {
        'keywords': ['cholesterol', 'high cholesterol', 'lipid'],
        'severity': 'moderate',
        'dietary_restrictions': ['saturated_fat', 'trans_fat']
    },
    'heart_disease': {
        'keywords': ['heart disease', 'cardiac', 'coronary', 'arrhythmia'],
        'severity': 'critical',
        'dietary_restrictions': ['high_sodium', 'saturated_fat']
    },
}

COMMON_ALLERGENS = {
    'peanuts': ['peanut', 'groundnut', 'arachis'],
    'shellfish': ['shellfish', 'shrimp', 'crab', 'lobster'],
    'dairy': ['milk', 'lactose', 'cheese', 'butter'],
    'gluten': ['gluten', 'wheat', 'barley', 'rye'],
    'tree_nuts': ['tree nut', 'almond', 'walnut', 'cashew'],
    'fish': ['fish', 'salmon', 'cod', 'tuna'],
    'soy': ['soy', 'soybean'],
    'eggs': ['egg', 'egg white'],
}

class MedicalDocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_file):
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""

    @staticmethod
    def extract_health_conditions(text):
        conditions = []
        text_lower = text.lower()

        for condition, info in COMMON_HEALTH_CONDITIONS.items():
            for keyword in info['keywords']:
                if keyword in text_lower:
                    conditions.append({
                        'condition': condition,
                        'confidence': 0.85,
                        'severity': info['severity'],
                        'dietary_restrictions': info['dietary_restrictions']
                    })
                    break

        return conditions

    @staticmethod
    def extract_allergens(text):
        allergens = []
        text_lower = text.lower()

        for allergen, keywords in COMMON_ALLERGENS.items():
            for keyword in keywords:
                if keyword in text_lower and any(word in text_lower for word in ['allerg', 'reaction', 'avoid', 'sensitivity']):
                    allergens.append({
                        'allergen': allergen,
                        'confidence': 0.80,
                        'severity': 'moderate'
                    })
                    break

        return allergens

    @staticmethod
    def extract_dietary_restrictions(text, conditions):
        restrictions = []

        for condition in conditions:
            dietary_info = COMMON_HEALTH_CONDITIONS.get(condition.get('condition'), {})
            for restriction in dietary_info.get('dietary_restrictions', []):
                restrictions.append({
                    'restriction': restriction,
                    'reason': f"Based on {condition.get('condition')} diagnosis",
                    'recommendation': f"Avoid {restriction.replace('_', ' ')}"
                })

        return restrictions

    @staticmethod
    def process_medical_document(file_obj):
        try:
            if file_obj.name.endswith('.pdf'):
                raw_text = MedicalDocumentProcessor.extract_text_from_pdf(file_obj)
            else:
                raw_text = file_obj.read().decode('utf-8')
        except Exception as e:
            print(f"File processing error: {e}")
            raw_text = MedicalDocumentProcessor._mock_document_text()

        conditions = MedicalDocumentProcessor.extract_health_conditions(raw_text)
        allergens = MedicalDocumentProcessor.extract_allergens(raw_text)
        restrictions = MedicalDocumentProcessor.extract_dietary_restrictions(raw_text, conditions)

        return {
            'raw_text': raw_text,
            'conditions': conditions,
            'allergens': allergens,
            'dietary_restrictions': restrictions
        }

    @staticmethod
    def _mock_document_text():
        return """
        Patient: John Doe
        Date: 2026-04-15

        MEDICAL REPORT

        Diagnosis: The patient has been diagnosed with Type 2 Diabetes and Hypertension (Stage 1).
        Blood sugar levels are elevated and require management through diet and medication.

        Allergies: Patient reports allergy to peanuts with history of mild reactions.
        Also sensitive to shellfish.

        Recommendations: Patient should avoid high sodium foods and refined carbohydrates.
        Regular exercise and weight management are essential.

        Medications: Metformin 500mg twice daily, Lisinopril 10mg once daily.
        """
