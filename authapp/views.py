from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from django.utils.crypto import get_random_string

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        token = get_random_string(30)
        user.profile.verification_token = token
        user.profile.save()
        send_mail(
            "Verify your email",
            f"Click the link to verify your account: http://localhost:8000/api/auth/verify/{token}/",
            "no-reply@example.com",
            [user.email]
        )

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, token):
        try:
            profile = User.objects.get(profile__verification_token=token).profile
            profile.user.is_active = True
            profile.verification_token = ''
            profile.user.save()
            profile.save()
            return Response({"message": "Email verified successfully!"})
        except Exception:
            return Response({"error": "Invalid or expired token"}, status=400)
