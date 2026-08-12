from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .admin_views import AdminUserViewSet, AdminDistrictViewSet, AdminEventViewSet

router = DefaultRouter()
router.register(r'users', AdminUserViewSet, basename='admin-users')
router.register(r'districts', AdminDistrictViewSet, basename='admin-districts')
router.register(r'events', AdminEventViewSet, basename='admin-events')

urlpatterns = [
    path('', include(router.urls)),
]
