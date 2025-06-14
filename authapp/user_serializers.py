from django.contrib.auth.models import User
from rest_framework import serializers

class UserListSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'role']

class UserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'role']
        read_only_fields = ['role']
