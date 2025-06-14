# views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import AmazonExclusive
from .serializers import AmazonExclusiveSerializer

from rest_framework.permissions import IsAuthenticated

class AmazonExclusiveViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AmazonExclusive.objects.all().order_by('-id')
    serializer_class = AmazonExclusiveSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Product deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user, modified_by=user)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(modified_by=user)

    @action(detail=False, methods=['post'], url_path='bulk_create')
    def bulk_create(self, request):
        # user = request.user if request.user.is_authenticated else None
        data = request.data
        if not isinstance(data, list):
            return Response({'detail': 'Expected a list of items.'}, status=status.HTTP_400_BAD_REQUEST)
        # for item in data:
        #     item['created_by'] = user.id if user else None
        #     item['modified_by'] = user.id if user else None
        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        serializer.save()