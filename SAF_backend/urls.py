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
# Import the serializer after Django is set up
from activities.serializers import CustomTokenObtainPairSerializer
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema view
schema_view = get_schema_view(
   openapi.Info(
      title="SAF API",
      default_version='v1',
      description="SAF API Documentation",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# ========================
# URL Patterns
# ========================
urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # Swagger/OpenAPI URLs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # REST Framework Login/Logout (for API auth)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Main API
    path('api/', include([
        # Include activities URLs with /api/ prefix
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

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)