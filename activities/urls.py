from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'messages', MessageContactViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
