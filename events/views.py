from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import Event, EventConfirmation, Attendance, EventImage
from .serializers import EventListSerializer, EventDetailSerializer, AttendeeSerializer, EventImageSerializer
from .filters import EventFilter


class IsOrganizerOrStaffOrReadOnly(permissions.BasePermission):
    """Only the event's organizer or staff can update/delete/manage images."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and (obj.organizer_id == user.id or user.is_staff))


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().select_related('district', 'organizer').prefetch_related('images')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description', 'venue_name', 'address']
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.action in ['create', 'going', 'confirm']:
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy', 'upload_images', 'remove_image']:
            return [permissions.IsAuthenticated(), IsOrganizerOrStaffOrReadOnly()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
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
                return qs.filter(Q(status='verified') | Q(organizer=user))
            return qs.filter(status='verified')
        return qs

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user, status='pending')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        event = serializer.instance

        images = request.FILES.getlist('images')
        for idx, img in enumerate(images):
            EventImage.objects.create(event=event, image=img, order=idx)

        output = EventDetailSerializer(event, context=self.get_serializer_context())
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        event = serializer.instance

        # Add any newly uploaded images
        images = request.FILES.getlist('images')
        if images:
            start_order = event.images.count()
            for idx, img in enumerate(images):
                EventImage.objects.create(event=event, image=img, order=start_order + idx)

        # Remove images by id, e.g. remove_image_ids=3&remove_image_ids=5
        remove_ids = request.data.getlist('remove_image_ids') if hasattr(request.data, 'getlist') \
            else request.data.get('remove_image_ids', [])
        if remove_ids:
            EventImage.objects.filter(event=event, id__in=remove_ids).delete()

        # self.get_object() above pulled `event` from a queryset with
        # prefetch_related('images'), which cached the pre-mutation image
        # list on the instance. Re-fetch fresh so the response reflects
        # the images we just added/removed instead of serving that cache.
        event = Event.objects.select_related('district', 'organizer').prefetch_related('images').get(pk=event.pk)
        output = EventDetailSerializer(event, context=self.get_serializer_context())
        return Response(output.data)

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

    @action(detail=True, methods=['post'], url_path='upload-images')
    def upload_images(self, request, pk=None):
        """Add one or more images to an existing event (organizer/staff only)."""
        event = self.get_object()
        images = request.FILES.getlist('images')
        if not images:
            return Response({'error': 'No images provided. Use the "images" field.'}, status=status.HTTP_400_BAD_REQUEST)

        start_order = event.images.count()
        created = []
        for idx, img in enumerate(images):
            created.append(EventImage.objects.create(event=event, image=img, order=start_order + idx))

        serializer = EventImageSerializer(created, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path=r'images/(?P<image_id>\d+)')
    def remove_image(self, request, pk=None, image_id=None):
        """Remove a single image from an event (organizer/staff only)."""
        event = self.get_object()
        deleted, _ = EventImage.objects.filter(event=event, id=image_id).delete()
        if not deleted:
            return Response({'error': 'Image not found for this event.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'Image removed successfully.'}, status=status.HTTP_200_OK)
