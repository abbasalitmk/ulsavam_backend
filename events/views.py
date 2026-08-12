from django.db import transaction
from django.utils import timezone
from datetime import datetime
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Event, EventConfirmation, Attendance
from .serializers import EventListSerializer, EventDetailSerializer, AttendeeSerializer
from .filters import EventFilter

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().select_related('district', 'organizer')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description', 'venue_name', 'address']

    def get_permissions(self):
        if self.action in ['create', 'going', 'confirm']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # For non-authenticated or normal users listing, show verified events AND user's own pending events
        if self.action == 'list':
            user = self.request.user
            verified_only = self.request.query_params.get('verified_only', None)
            if verified_only and verified_only.lower() == 'true':
                return qs.filter(status='verified')
            if user and user.is_authenticated:
                return qs.filter(models.Q(status='verified') | models.Q(organizer=user))
            return qs.filter(status='verified')
        return qs

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user, status='pending')

    @action(detail=False, methods=['get'], url_path='happening-now')
    def happening_now(self, request):
        today = timezone.now().date()
        district_param = request.query_params.get('district')
        qs = self.get_queryset().filter(event_date=today, status='verified')
        if district_param:
            if district_param.isdigit():
                qs = qs.filter(district__id=district_param)
            else:
                qs = qs.filter(district__slug=district_param)
        
        serializer = EventListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='calendar')
    def calendar(self, request):
        district_param = request.query_params.get('district')
        month_param = request.query_params.get('month')  # format: YYYY-MM
        
        qs = self.get_queryset().filter(status='verified')
        if district_param:
            if district_param.isdigit():
                qs = qs.filter(district__id=district_param)
            else:
                qs = qs.filter(district__slug=district_param)
                
        if month_param:
            try:
                dt = datetime.strptime(month_param, '%Y-%m')
                qs = qs.filter(event_date__year=dt.year, event_date__month=dt.month)
            except ValueError:
                pass

        serializer = EventListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='going')
    def going(self, request, pk=None):
        event = self.get_object()
        user = request.user

        attendance, created = Attendance.objects.get_or_create(event=event, user=user)
        if not created:
            attendance.delete()
            is_going = False
            message = "Removed from Going list."
        else:
            is_going = True
            message = "Marked as Going!"

        return Response({
            'message': message,
            'is_going': is_going,
            'going_count': event.going_count
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm(self, request, pk=None):
        user = request.user
        
        with transaction.atomic():
            event = Event.objects.select_for_update().get(pk=pk)
            
            confirmation, created = EventConfirmation.objects.get_or_create(event=event, user=user)
            if not created:
                return Response({
                    'message': 'You have already verified this event.',
                    'confirmations_count': event.confirmations_count,
                    'status': event.status
                }, status=status.HTTP_200_OK)

            confirmations_count = event.confirmations.count()
            # 3-Confirmation gate auto-flip logic
            if confirmations_count >= 3 and event.status == 'pending':
                event.status = 'verified'
                event.save(update_fields=['status'])

        return Response({
            'message': 'Event confirmation recorded successfully!',
            'confirmations_count': event.confirmations_count,
            'status': event.status
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='attendees')
    def attendees(self, request, pk=None):
        event = self.get_object()
        attendances = Attendance.objects.filter(event=event).select_related('user')
        serializer = AttendeeSerializer(attendances, many=True, context={'request': request})
        return Response(serializer.data)
