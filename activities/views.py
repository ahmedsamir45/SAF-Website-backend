from django.shortcuts import render
from .models import *
from .serializer import *
# Create your views here.
# Views
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class UserViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for the `User` model.
    Provides CRUD (Create, Retrieve, Update, Delete) operations for `User` instances.
    - `queryset`: Specifies the queryset to be used, which includes all `User` instances.
    - `serializer_class`: Specifies the serializer to be used, which is `UserSerializer`.
    - `permission_classes`: Restricts access to authenticated users only.
    """
    queryset = User.objects.all()  # Queryset to fetch all User instances
    serializer_class = UserSerializer  # Serializer to handle User data
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users

class ProgramViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for the `Program` model.
    Provides CRUD (Create, Retrieve, Update, Delete) operations for `Program` instances.
    - `queryset`: Specifies the queryset to be used, which includes all `Program` instances.
    - `serializer_class`: Specifies the serializer to be used, which is `ProgramSerializer`.
    - `permission_classes`: Restricts access to authenticated users only.
    """
    queryset = Program.objects.all()  # Queryset to fetch all Program instances
    serializer_class = ProgramSerializer  # Serializer to handle Program data
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users

class MessageContactViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for the `MessageContact` model.
    Provides CRUD (Create, Retrieve, Update, Delete) operations for `MessageContact` instances.
    - `queryset`: Specifies the queryset to be used, which includes all `MessageContact` instances.
    - `serializer_class`: Specifies the serializer to be used, which is `MessageContactSerializer`.
    - `permission_classes`: Restricts access to authenticated users only.
    """
    queryset = MessageContact.objects.all()  # Queryset to fetch all MessageContact instances
    serializer_class = MessageContactSerializer  # Serializer to handle MessageContact data
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users