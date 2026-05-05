from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import MedicalReport, ExtractedHealthInfo
from .nlp_service import MedicalDocumentProcessor

class MedicalProcessingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_health_condition_extraction(self):
        text = "Patient has been diagnosed with Type 2 Diabetes"
        conditions = MedicalDocumentProcessor.extract_health_conditions(text)
        self.assertGreater(len(conditions), 0)
        self.assertEqual(conditions[0]['condition'], 'diabetes')

    def test_allergen_extraction(self):
        text = "Patient is allergic to peanuts"
        allergens = MedicalDocumentProcessor.extract_allergens(text)
        self.assertGreater(len(allergens), 0)

    def test_dietary_restrictions_extraction(self):
        text = "Patient diagnosed with hypertension"
        conditions = [{'condition': 'hypertension', 'severity': 'high'}]
        restrictions = MedicalDocumentProcessor.extract_dietary_restrictions(text, conditions)
        self.assertGreater(len(restrictions), 0)

    def test_medical_report_creation(self):
        report = MedicalReport.objects.create(
            user=self.user,
            status='completed'
        )
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.status, 'completed')
