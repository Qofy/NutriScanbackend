from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodAnalysisViewSet, FoodItemViewSet

router = DefaultRouter()
router.register(r'analysis', FoodAnalysisViewSet, basename='food-analysis')
router.register(r'items', FoodItemViewSet, basename='food-item')

urlpatterns = [
    path('analysis/manual-analyze/', FoodAnalysisViewSet.as_view({'post': 'manual_analyze'}), name='food-analysis-manual-analyze'),
    path('', include(router.urls)),
]
