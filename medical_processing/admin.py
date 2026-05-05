from django.contrib import admin
from .models import MedicalReport, ExtractedHealthInfo, Allergy, DietaryRestriction

@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at', 'status')
    list_filter = ('status', 'uploaded_at')
    search_fields = ('user__username',)

@admin.register(ExtractedHealthInfo)
class ExtractedHealthInfoAdmin(admin.ModelAdmin):
    list_display = ('condition_name', 'severity', 'confidence')
    search_fields = ('condition_name',)

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('allergen', 'severity', 'confidence')
    search_fields = ('allergen',)

@admin.register(DietaryRestriction)
class DietaryRestrictionAdmin(admin.ModelAdmin):
    list_display = ('restriction', 'reason')
    search_fields = ('restriction',)
