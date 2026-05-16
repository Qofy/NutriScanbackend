from django.urls import path
from .admin_views import AdminViewSet

admin_view = AdminViewSet.as_view

urlpatterns = [
    path('stats/', admin_view({'get': 'stats'}), name='admin-stats'),
    path('users/', admin_view({'get': 'list_users'}), name='admin-users'),
    path('users/<int:pk>/role/', admin_view({'put': 'update_role'}), name='admin-update-role'),
    path('scans/', admin_view({'get': 'list_scans'}), name='admin-scans'),
    path('reports/', admin_view({'get': 'list_reports'}), name='admin-reports'),
]
