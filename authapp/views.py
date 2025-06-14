from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, EmailOrUsernameTokenObtainPairSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'detail': 'Only admin users can register new users.'}, status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = True
        user.save()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailOrUsernameTokenObtainPairSerializer

