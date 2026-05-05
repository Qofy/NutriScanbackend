from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/food/', include('food_recognition.urls')),
    path('api/medical/', include('medical_processing.urls')),
    path('api/recommendations/', include('recommendations.urls')),
    path('api/profile/', include('user_profile.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
