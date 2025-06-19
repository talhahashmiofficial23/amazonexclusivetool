# views.py
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import AmazonExclusive, ProductPriceHistory
from .serializers import AmazonExclusiveSerializer, ProductPriceHistorySerializer, CreateProductPriceHistorySerializer

from rest_framework.permissions import IsAuthenticated

class AmazonExclusiveViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AmazonExclusive.objects.all().order_by('-id')
    serializer_class = AmazonExclusiveSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'success'}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user, modified_by=user)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(modified_by=user)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Return all AmazonExclusive records including price histories for dashboard."""
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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


class ProductPriceHistoryViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    API endpoint for creating price history entries.
    If the AmazonExclusive doesn't exist, it will be created.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CreateProductPriceHistorySerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new price history entry.
        If amazon_exclusive is not provided, a new AmazonExclusive will be created using product_data.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        price_history = serializer.save()
        
        # Return the created price history with full details
        response_serializer = ProductPriceHistorySerializer(price_history)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )