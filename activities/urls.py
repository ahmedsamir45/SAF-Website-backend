# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    UserViewSet,
    ProgramViewSet,
    ProgramImageViewSet,
    FavoriteViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework_nested import routers
from .views import (
    UserViewSet,
    ProgramViewSet,
    ProgramImageViewSet,
    FavoriteViewSet,
    MessageContactViewSet
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'programs', ProgramViewSet, basename='program')
router.register(r'messages', MessageContactViewSet, basename='message')

# Nested routers for programs and users
programs_router = routers.NestedSimpleRouter(router, r'programs', lookup='program')
programs_router.register(r'images', ProgramImageViewSet, basename='program-images')

users_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
users_router.register(r'favorites', FavoriteViewSet, basename='user-favorites')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(programs_router.urls)),
    path('', include(users_router.urls)),
]