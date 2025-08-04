# views.py
from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import OuterRef, Subquery, Max
from django_filters.rest_framework import DjangoFilterBackend
from .models import AmazonExclusive, ProductPriceHistory, MasterSeason, DepartmentDivision, Category, Subclass
from .serializers import (
    AmazonExclusiveSerializer, ProductPriceHistorySerializer, CreateProductPriceHistorySerializer,
    MasterSeasonSerializer, DepartmentDivisionSerializer, CategorySerializer, SubclassSerializer
)

from rest_framework.permissions import IsAuthenticated

class AmazonExclusiveViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AmazonExclusive.objects.all()
    serializer_class = AmazonExclusiveSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        'master_season': ['exact', 'in'],
        'dept_div': ['exact', 'in'],
        'category': ['exact', 'in'],
        'subclass': ['exact', 'in'],
    }
    ordering_fields = ['list_price', 'id']
    ordering = ['-id']  # Default ordering

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get price range parameters
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        # Apply price range filters if provided
        if min_price is not None:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(list_price__gte=min_price)
            except (ValueError, TypeError):
                pass
                
        if max_price is not None:
            try:
                max_price = float(max_price)
                queryset = queryset.filter(list_price__lte=max_price)
            except (ValueError, TypeError):
                pass
                
        return queryset
        
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
        """
        Return all AmazonExclusive records including price histories for dashboard, paginated.
        
        Filtering is supported on the following fields:
        - master_season: Filter by master season ID (exact or in list)
        - dept_div: Filter by department division ID (exact or in list)
        - category: Filter by category ID (exact or in list)
        - subclass: Filter by subclass ID (exact or in list)
        - min_price: Filter by minimum list price
        - max_price: Filter by maximum list price
        
        Sorting is supported using:
        - sort_by=list_price or sort_by=price_history
        - sort_order=asc or sort_order=desc (default: desc)
        
        Example: 
        - /api/amazon-exclusives/dashboard/?master_season=1&dept_div=2
        - /api/amazon-exclusives/dashboard/?sort_by=price_history&sort_order=asc
        - /api/amazon-exclusives/dashboard/?min_price=100&max_price=1000
        """
        # Apply filters from query parameters
        master_season = request.query_params.getlist('master_season')
        dept_div = request.query_params.getlist('dept_div')
        category = request.query_params.getlist('category')
        subclass = request.query_params.getlist('subclass')
        
        # Get price range parameters
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        
        # Get sort parameters
        sort_by = request.query_params.get('sort_by')
        sort_order = request.query_params.get('sort_order', 'desc').lower()
        
        # Start with base queryset
        queryset = self.get_queryset()
        
        # Apply filters
        if master_season:
            queryset = queryset.filter(master_season_id__in=master_season)
        if dept_div:
            queryset = queryset.filter(dept_div_id__in=dept_div)
        if category:
            queryset = queryset.filter(category_id__in=category)
        if subclass:
            queryset = queryset.filter(subclass_id__in=subclass)
            
        # Apply price range filters if provided
        if min_price is not None:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(list_price__gte=min_price)
            except (ValueError, TypeError):
                pass
                
        if max_price is not None:
            try:
                max_price = float(max_price)
                queryset = queryset.filter(list_price__lte=max_price)
            except (ValueError, TypeError):
                pass
            
        # Handle sorting
        if sort_by == 'price_history':
            # For dashboard, we need to handle the subquery again since we're using select_related
            latest_price = ProductPriceHistory.objects.filter(
                amazon_exclusive=OuterRef('pk')
            ).order_by('-created_at').values('new_price')[:1]
            
            from django.db.models import DecimalField
            queryset = queryset.annotate(
                latest_price=Subquery(latest_price, output_field=DecimalField(max_digits=50, decimal_places=2))
            )
            
            order_by = 'latest_price' if sort_order == 'asc' else '-latest_price'
            queryset = queryset.order_by(order_by)
        
        # Apply select_related and prefetch_related
        qs = self.filter_queryset(
            queryset
            .select_related('master_season', 'dept_div', 'category', 'subclass')
            .prefetch_related('price_history')
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='bulk_create')
    def bulk_create(self, request):
        from .models import MasterSeason, DepartmentDivision, Category, Subclass
        data = request.data
        if not isinstance(data, list):
            return Response({'detail': 'Expected a list of items.'}, status=status.HTTP_400_BAD_REQUEST)

        fk_map = {
            'master_season': MasterSeason,
            'dept_div': DepartmentDivision,
            'category': Category,
            'subclass': Subclass,
        }
        for item in data:
            # Clean planned_discount and planned_asp
            for field in ['planned_discount', 'planned_asp']:
                val = item.get(field)
                if isinstance(val, str):
                    try:
                        # Try to convert to float, if fails set to 0
                        float(val)
                    except Exception:
                        item[field] = 0
            # Foreign key resolution/creation
            for fk_field, model in fk_map.items():
                val = item.get(fk_field)
                if val and isinstance(val, str):
                    obj, _ = model.objects.get_or_create(name=val)
                    item[fk_field] = obj.id
        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        serializer.save()


class BaseDropdownViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['name']
    
    def get_queryset(self):
        queryset = self.queryset.order_by('name')
        
        # Handle search by name
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        model_name = self.queryset.model._meta.verbose_name
        return Response(
            {"message": f"{model_name} created successfully", "data": response.data},
            status=status.HTTP_201_CREATED
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        model_name = self.queryset.model._meta.verbose_name
        self.perform_destroy(instance)
        return Response(
            {"message": f"{model_name} deleted successfully"},
            status=status.HTTP_200_OK
        )


class MasterSeasonViewSet(BaseDropdownViewSet):
    queryset = MasterSeason.objects.all()
    serializer_class = MasterSeasonSerializer


class DepartmentDivisionViewSet(BaseDropdownViewSet):
    queryset = DepartmentDivision.objects.all()
    serializer_class = DepartmentDivisionSerializer


class CategoryViewSet(BaseDropdownViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubclassViewSet(BaseDropdownViewSet):
    queryset = Subclass.objects.all()
    serializer_class = SubclassSerializer


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

    @action(detail=False, methods=['get'], url_path='products')
    def list_products(self, request):
        """
        List all AmazonExclusive products, paginated.
        Supports dynamic ?page_size= parameter for this endpoint only.
        """
        queryset = AmazonExclusive.objects.all().order_by('-id')

        # Dynamically set page_size for this action only
        try:
            page_size = int(request.query_params.get('page_size', 0))
            if page_size > 0:
                self.paginator.page_size = page_size
        except (ValueError, TypeError, AttributeError):
            pass  # fallback to default

        page = self.paginate_queryset(queryset)
        serializer = AmazonExclusiveSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['post'], url_path='bulk_create_history')
    def bulk_create_history(self, request):
        """
        Create price history entries for multiple product IDs, each with its own price.
        Expects: { "items": [ {"id": 1, "new_price": 100}, ... ] }
        """
        items = request.data.get('items', [])
        if not isinstance(items, list) or not items:
            return Response({'detail': 'items (list of {id, new_price}) is required.'}, status=400)

        histories = []
        for entry in items:
            product_id = entry.get('id')
            new_price = entry.get('new_price')
            if product_id is None or new_price is None:
                continue
            try:
                product = AmazonExclusive.objects.get(id=product_id)
                old_price = product.list_price or 0
                if old_price != new_price:
                    product.list_price = new_price
                    product.save(skip_price_history=True)
                    history = ProductPriceHistory.objects.create(
                        amazon_exclusive=product,
                        old_price=old_price,
                        new_price=new_price
                    )
                    histories.append(ProductPriceHistorySerializer(history).data)
            except AmazonExclusive.DoesNotExist:
                continue

        return Response({'created_histories': histories}, status=201)

