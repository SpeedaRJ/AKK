from .models import User
from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    sex = serializers.CharField()
    age = serializers.IntegerField()
    chapters = serializers.CharField()
