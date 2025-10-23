from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from django.conf import settings
from django.conf.urls.static import static
from activities.serializers import CustomTokenObtainPairSerializer

# ========================
# Swagger Schema View
# ========================
schema_view = get_schema_view(
    openapi.Info(
        title="SAF Backend API",
        default_version='v1',
        description="API documentation for SAF Backend",
        terms_of_service="https://www.your-terms-of-service.com/",
        contact=openapi.Contact(email="ahmedsamer6788@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# ========================
# URL Patterns
# ========================
urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Swagger / Redoc Docs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),

    # REST Framework Login/Logout (for Swagger auth fix)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Main API
    path('api/', include([
        # Activities app endpoints
        path('', include('activities.urls')),

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
