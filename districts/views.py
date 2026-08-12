from rest_framework import viewsets, permissions
from .models import District
from .serializers import DistrictSerializer

class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # Return all 14 districts without pagination
