from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username'

    def validate(self, attrs):
        credentials = {
            'username': attrs.get('username'),
            'password': attrs.get('password')
        }
        user = None
        # Try authenticating with username
        user = authenticate(username=credentials['username'], password=credentials['password'])
        if not user:
            # Try authenticating with email
            try:
                user_obj = User.objects.get(email=credentials['username'])
                user = authenticate(username=user_obj.username, password=credentials['password'])
            except User.DoesNotExist:
                pass
        if user is None:
            raise serializers.ValidationError('No active account found with the given credentials')
        token_data = super().validate({'username': user.username, 'password': credentials['password']})
        # Return token and user details
        return {
            'token': token_data['access'],
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'role': getattr(user.profile, 'role', None),
            }
        }


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn’t match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.is_active = False  # Require email verification
        user.save()
        return user
