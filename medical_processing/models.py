from django.db import models
from django.contrib.auth.models import User

class MedicalReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.FileField(upload_to='medical_reports/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    extracted_data = models.JSONField(default=dict)
    raw_text = models.TextField(blank=True)
    processing_error = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Medical Report - {self.user.username} - {self.uploaded_at}"


class ExtractedHealthInfo(models.Model):
    report = models.ForeignKey(MedicalReport, on_delete=models.CASCADE, related_name='health_info')
    condition_name = models.CharField(max_length=255)
    confidence = models.FloatField()
    description = models.TextField()
    severity = models.CharField(max_length=50, default='moderate')

    def __str__(self):
        return f"{self.condition_name} - {self.confidence}%"


class Allergy(models.Model):
    report = models.ForeignKey(MedicalReport, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField(max_length=255)
    reaction_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=50)
    confidence = models.FloatField()

    class Meta:
        unique_together = ('report', 'allergen')

    def __str__(self):
        return f"{self.allergen} - {self.severity}"


class DietaryRestriction(models.Model):
    report = models.ForeignKey(MedicalReport, on_delete=models.CASCADE, related_name='dietary_restrictions')
    restriction = models.CharField(max_length=255)
    reason = models.TextField()
    recommendation = models.TextField()

    def __str__(self):
        return f"{self.restriction} ({self.reason})"
