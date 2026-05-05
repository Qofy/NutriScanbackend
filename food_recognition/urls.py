from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodAnalysisViewSet, FoodItemViewSet

router = DefaultRouter()
router.register(r'analysis', FoodAnalysisViewSet, basename='food-analysis')
router.register(r'items', FoodItemViewSet, basename='food-item')

urlpatterns = [
    path('', include(router.urls)),
]
