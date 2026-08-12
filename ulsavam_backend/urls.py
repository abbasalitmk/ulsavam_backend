from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from core import admin_panel_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Public API
    path('api/auth/', include('users.urls')),
    path('api/districts/', include('districts.urls')),
    path('api/events/', include('events.urls')),
    path('api/notifications/', include('notifications.urls')),

    # Admin Dashboard API
    path('api/admin/', include('core.admin_urls')),

    # SuperAdmin Panel (Custom HTML/JS)
    path('superadmin/', admin_panel_views.SuperAdminPanelView.as_view(), name='superadmin-dashboard'),
    path('superadmin/login/', admin_panel_views.admin_login_page, name='superadmin-login'),
    path('api/admin/login/', admin_panel_views.admin_login_api, name='admin-login-api'),

    # OpenAPI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
