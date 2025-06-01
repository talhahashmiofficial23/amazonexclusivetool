# serializers.py

from rest_framework import serializers
from .models import AmazonExclusive

class AmazonExclusiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonExclusive
        fields = '__all__'
