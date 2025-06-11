# views.py

from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import AmazonExclusive
from .serializers import AmazonExclusiveSerializer

from rest_framework.permissions import IsAuthenticated

class AmazonExclusiveViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AmazonExclusive.objects.all().order_by('-id')
    serializer_class = AmazonExclusiveSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user, modified_by=user)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(modified_by=user)