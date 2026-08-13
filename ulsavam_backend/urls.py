from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
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

# Serve uploaded media even outside DEBUG. Note: django.conf.urls.static.static()
# silently no-ops unless settings.DEBUG is True (hard-coded inside Django itself,
# regardless of any guard around the call), so it can't be used here - we call
# the underlying view directly instead. Render's free web service has no
# separate static file server / nginx in front, so Django itself must serve
# /media/ or every profile_pic / event image URL 404s in production.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
