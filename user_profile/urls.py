from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserHealthProfileViewSet, DailyTrackingViewSet, SavedFoodViewSet, CurrentUserViewSet

router = DefaultRouter()
router.register(r'daily-tracking', DailyTrackingViewSet, basename='daily-tracking')
router.register(r'saved-foods', SavedFoodViewSet, basename='saved-food')
router.register(r'user', CurrentUserViewSet, basename='current-user')

urlpatterns = [
    path('health/', UserHealthProfileViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'post': 'create_profile'
    })),
    path('health/conditions/', UserHealthProfileViewSet.as_view({
        'post': 'update_health_conditions'
    })),
    path('health/allergies/', UserHealthProfileViewSet.as_view({
        'post': 'update_allergies'
    })),
    path('', include(router.urls)),
]
