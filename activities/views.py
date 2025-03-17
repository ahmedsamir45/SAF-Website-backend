from django.shortcuts import render
from .models import *
from .serializer import *
# Create your views here.
# Views
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]

class MessageContactViewSet(viewsets.ModelViewSet):
    queryset = MessageContact.objects.all()
    serializer_class = MessageContactSerializer
    permission_classes = [IsAuthenticated]