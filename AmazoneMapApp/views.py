# views.py

from rest_framework import viewsets
from .models import AmazonExclusive
from .serializers import AmazonExclusiveSerializer

class AmazonExclusiveViewSet(viewsets.ModelViewSet):
    queryset = AmazonExclusive.objects.all()
    serializer_class = AmazonExclusiveSerializer



# df = pd.read_excel("AMAZON EXCLUSIVES_MAP TOOL SEND_MAY 2025[39].xlsx", engine="openpyxl", skiprows=1)