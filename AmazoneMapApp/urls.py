# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AmazonExclusiveViewSet, ProductPriceHistoryViewSet,
    MasterSeasonViewSet, DepartmentDivisionViewSet,
    CategoryViewSet, SubclassViewSet
)

router = DefaultRouter()
router.register(r'amazon-exclusives', AmazonExclusiveViewSet)
router.register(r'price-history', ProductPriceHistoryViewSet, basename='price-history')
router.register(r'master-seasons', MasterSeasonViewSet, basename='master-season')
router.register(r'department-divisions', DepartmentDivisionViewSet, basename='department-division')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'subclasses', SubclassViewSet, basename='subclass')

urlpatterns = [
    path('', include(router.urls)),
]
