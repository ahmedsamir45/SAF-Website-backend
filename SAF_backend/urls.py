from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.views.generic import RedirectView
from activities.serializers import CustomTokenObtainPairSerializer
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

# ========================
# URL Patterns
# ========================
# Serve media files in development
urlpatterns = []

# Add media URL patterns in development or when DEBUG is True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, use the following pattern
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
    ]

# Main URL patterns
urlpatterns += [
    # Admin Panel
    path('admin/', admin.site.urls),

    # API Schema and Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # REST Framework Login/Logout (for API auth)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Main API
    path('api/', include([
        # Activities app endpoints
        path('', include('activities.urls')),
        # Media files serving (development and production)
        re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
        # Ensure media URLs work with or without trailing slashes
        re_path(r'^media/(?P<path>.*)/$', static_serve, {'document_root': settings.MEDIA_ROOT}),

        # Authentication
        path('auth/token/',
             TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer),
             name='token_obtain_pair'),
        path('auth/token/refresh/',
             TokenRefreshView.as_view(),
             name='token_refresh'),
        path('auth/token/verify/',
             TokenVerifyView.as_view(),
             name='token_verify'),

        # Djoser authentication routes
        path('auth/', include('djoser.urls')),
        path('auth/', include('djoser.urls.jwt')),
    ])),
]

# ========================
# Media Files (Development)
# ========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
