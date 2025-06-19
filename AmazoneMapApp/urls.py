# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AmazonExclusiveViewSet, ProductPriceHistoryViewSet

router = DefaultRouter()
router.register(r'amazon-exclusives', AmazonExclusiveViewSet)
router.register(r'price-history', ProductPriceHistoryViewSet, basename='price-history')

urlpatterns = [
    path('', include(router.urls)),
]
