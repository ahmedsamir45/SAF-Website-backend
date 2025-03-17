from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the `User` model.
    This serializer includes all fields of the `User` model.
    It is used to convert `User` model instances into JSON format and vice versa.
    """
    class Meta:
        model = User  # Specifies the model to be serialized
        fields = '__all__'  # Includes all fields from the model

class ProgramSerializer(serializers.ModelSerializer):
    """
    Serializer for the `Program` model.
    This serializer includes all fields of the `Program` model.
    It is used to convert `Program` model instances into JSON format and vice versa.
    """
    class Meta:
        model = Program  # Specifies the model to be serialized
        fields = '__all__'  # Includes all fields from the model

class RequirementSerializer(serializers.ModelSerializer):
    """
    Serializer for the `Requirement` model.
    This serializer includes all fields of the `Requirement` model.
    It is used to convert `Requirement` model instances into JSON format and vice versa.
    """
    class Meta:
        model = Requirement  # Specifies the model to be serialized
        fields = '__all__'  # Includes all fields from the model

class FavoriteSerializer(serializers.ModelSerializer):
    """
    Serializer for the `Favorite` model.
    This serializer includes all fields of the `Favorite` model.
    It is used to convert `Favorite` model instances into JSON format and vice versa.
    """
    class Meta:
        model = Favorite  # Specifies the model to be serialized
        fields = '__all__'  # Includes all fields from the model

class EmailLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the `EmailLog` model.
    This serializer includes all fields of the `EmailLog` model.
    It is used to convert `EmailLog` model instances into JSON format and vice versa.
    """
    class Meta:
        model = EmailLog  # Specifies the model to be serialized
        fields = '__all__'  # Includes all fields from the model

class MessageContactSerializer(serializers.ModelSerializer):
    """
    Serializer for the `MessageContact` model.
    This serializer includes all fields of the `MessageContact` model.
    It is used to convert `MessageContact` model instances into JSON format and vice versa.
    """
    class Meta:
        model = MessageContact  # Specifies the model to be serialized
        fields = '__all__'  # Includes all fields from the model