# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AmazonExclusiveViewSet

router = DefaultRouter()
router.register(r'amazon-exclusives', AmazonExclusiveViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
