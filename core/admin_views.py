from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from users.models import User
from districts.models import District
from events.models import Event, EventConfirmation, Attendance, EventImage
from .admin_serializers import (
    AdminUserSerializer, AdminDistrictSerializer,
    AdminEventListSerializer, AdminEventDetailSerializer
)


class IsAdmin(permissions.BasePermission):
    """Permission to check if user is admin"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class AdminUserViewSet(viewsets.ModelViewSet):
    """Admin viewset for user management"""
    queryset = User.objects.all().select_related('district')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['email', 'phone_number', 'display_name']
    ordering_fields = ['created_at', 'display_name', 'email']
    ordering = ['-created_at']
    filterset_fields = ['district', 'is_staff', 'preferred_language']

    @action(detail=True, methods=['post'])
    def make_staff(self, request, pk=None):
        """Make a user staff member"""
        user = self.get_object()
        user.is_staff = True
        user.save()
        return Response({'status': f'{user.display_name} is now staff'})

    @action(detail=True, methods=['post'])
    def remove_staff(self, request, pk=None):
        """Remove staff privileges"""
        user = self.get_object()
        user.is_staff = False
        user.save()
        return Response({'status': f'{user.display_name} is no longer staff'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        total_users = User.objects.count()
        staff_users = User.objects.filter(is_staff=True).count()
        users_with_events = User.objects.filter(
            event_confirmations__isnull=False
        ).distinct().count()

        return Response({
            'total_users': total_users,
            'staff_members': staff_users,
            'users_with_event_interests': users_with_events,
            'regular_users': total_users - staff_users
        })

    @action(detail=True, methods=['get'])
    def activity(self, request, pk=None):
        """Get user activity summary"""
        user = self.get_object()
        confirmations = user.event_confirmations.count()
        attendances = user.attendances.count()
        organized_events = Event.objects.filter(organizer=user).count()

        return Response({
            'user_id': user.id,
            'user_name': user.display_name,
            'confirmations': confirmations,
            'attendances': attendances,
            'organized_events': organized_events,
            'total_interactions': confirmations + attendances + organized_events
        })


class AdminDistrictViewSet(viewsets.ModelViewSet):
    """Admin viewset for district management"""
    queryset = District.objects.all()
    serializer_class = AdminDistrictSerializer
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'id']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Get all events in a district with filters"""
        district = self.get_object()
        events = district.events.all()

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            events = events.filter(status=status_filter)

        category_filter = request.query_params.get('category')
        if category_filter:
            events = events.filter(category=category_filter)

        featured_only = request.query_params.get('featured_only', 'false').lower() == 'true'
        if featured_only:
            events = events.filter(is_featured=True)

        serializer = AdminEventListSerializer(events, many=True)
        return Response({
            'district': district.name,
            'total_events': events.count(),
            'events': serializer.data
        })

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get all users in a district"""
        district = self.get_object()
        users = district.users.all()

        is_staff_filter = request.query_params.get('is_staff')
        if is_staff_filter:
            is_staff_filter = is_staff_filter.lower() == 'true'
            users = users.filter(is_staff=is_staff_filter)

        serializer = AdminUserSerializer(users, many=True)
        return Response({
            'district': district.name,
            'total_users': users.count(),
            'users': serializer.data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get district statistics"""
        districts = District.objects.all()
        stats = []

        for district in districts:
            stats.append({
                'district_name': district.name,
                'total_events': district.events.count(),
                'total_users': district.users.count(),
                'verified_events': district.events.filter(status='verified').count(),
                'featured_events': district.events.filter(is_featured=True).count(),
            })

        return Response({
            'total_districts': districts.count(),
            'districts': stats
        })


class AdminEventViewSet(viewsets.ModelViewSet):
    """Admin viewset for event management"""
    queryset = Event.objects.all().select_related('district', 'organizer').prefetch_related('images')
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'venue_name', 'address']
    ordering_fields = ['event_date', 'created_at', 'title']
    ordering = ['-event_date']
    filterset_fields = ['district', 'category', 'status', 'is_featured']
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        """Use detail serializer for retrieve/create/update (list needs the full writable fields); list uses the lighter serializer"""
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return AdminEventDetailSerializer
        return AdminEventListSerializer

    def perform_create(self, serializer):
        if serializer.validated_data.get('organizer'):
            serializer.save()
        else:
            serializer.save(organizer=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        event = serializer.instance

        images = request.FILES.getlist('images')
        for idx, img in enumerate(images):
            EventImage.objects.create(event=event, image=img, order=idx)

        output = AdminEventDetailSerializer(event, context=self.get_serializer_context())
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        event = serializer.instance

        images = request.FILES.getlist('images')
        if images:
            start_order = event.images.count()
            for idx, img in enumerate(images):
                EventImage.objects.create(event=event, image=img, order=start_order + idx)

        remove_ids = request.data.getlist('remove_image_ids') if hasattr(request.data, 'getlist') \
            else request.data.get('remove_image_ids', [])
        if remove_ids:
            EventImage.objects.filter(event=event, id__in=remove_ids).delete()

        # self.get_object() above pulled `event` from a queryset with
        # prefetch_related('images'), which cached the pre-mutation image
        # list on the instance. Re-fetch fresh so the response reflects
        # the images we just added/removed instead of serving that cache.
        event = Event.objects.select_related('district', 'organizer').prefetch_related('images').get(pk=event.pk)
        output = AdminEventDetailSerializer(event, context=self.get_serializer_context())
        return Response(output.data)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a pending event"""
        event = self.get_object()
        if event.status == 'verified':
            return Response(
                {'error': 'Event is already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        event.status = 'verified'
        event.save()
        return Response({'status': f'Event "{event.title}" verified successfully'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a pending event"""
        event = self.get_object()
        reason = request.data.get('reason', 'No reason provided')
        if event.status == 'rejected':
            return Response(
                {'error': 'Event is already rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        event.status = 'rejected'
        event.save()
        return Response({
            'status': f'Event "{event.title}" rejected',
            'reason': reason
        })

    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        """Toggle featured status of an event"""
        event = self.get_object()
        event.is_featured = not event.is_featured
        event.save()
        return Response({
            'status': 'success',
            'event_id': event.id,
            'is_featured': event.is_featured
        })

    @action(detail=True, methods=['get'])
    def confirmations(self, request, pk=None):
        """Get all confirmations for an event"""
        event = self.get_object()
        confirmations = EventConfirmation.objects.filter(
            event=event
        ).select_related('user').order_by('-created_at')

        data = [
            {
                'id': c.id,
                'user_id': c.user.id,
                'user_name': c.user.display_name,
                'user_email': c.user.email,
                'user_district': c.user.district.name if c.user.district else None,
                'confirmed_at': c.created_at
            }
            for c in confirmations
        ]

        return Response({
            'event_id': event.id,
            'event_title': event.title,
            'total_confirmations': confirmations.count(),
            'confirmations': data
        })

    @action(detail=True, methods=['get'])
    def attendees(self, request, pk=None):
        """Get all attendees for an event"""
        event = self.get_object()
        attendances = Attendance.objects.filter(
            event=event
        ).select_related('user').order_by('-created_at')

        data = [
            {
                'id': a.id,
                'user_id': a.user.id,
                'user_name': a.user.display_name,
                'user_email': a.user.email,
                'user_district': a.user.district.name if a.user.district else None,
                'marked_at': a.created_at
            }
            for a in attendances
        ]

        return Response({
            'event_id': event.id,
            'event_title': event.title,
            'total_attendees': attendances.count(),
            'attendees': data
        })

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming events"""
        days = int(request.query_params.get('days', 30))
        cutoff_date = timezone.now().date() + timedelta(days=days)

        events = Event.objects.filter(
            event_date__gte=timezone.now().date(),
            event_date__lte=cutoff_date,
            status='verified'
        ).order_by('event_date')

        serializer = AdminEventListSerializer(events, many=True)
        return Response({
            'days_ahead': days,
            'total_upcoming': events.count(),
            'events': serializer.data
        })

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending events awaiting verification"""
        events = Event.objects.filter(
            status='pending'
        ).order_by('-created_at')

        serializer = AdminEventListSerializer(events, many=True)
        return Response({
            'total_pending': events.count(),
            'events': serializer.data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get event statistics"""
        total_events = Event.objects.count()
        verified = Event.objects.filter(status='verified').count()
        pending = Event.objects.filter(status='pending').count()
        rejected = Event.objects.filter(status='rejected').count()
        featured = Event.objects.filter(is_featured=True).count()

        # Events by category
        categories = {}
        for event in Event.objects.values('category').distinct():
            cat = event['category']
            categories[cat] = Event.objects.filter(category=cat).count()

        # Events by district
        districts = {}
        for event in Event.objects.values('district__name').distinct():
            dist = event['district__name']
            districts[dist] = Event.objects.filter(district__name=dist).count()

        return Response({
            'total_events': total_events,
            'status_breakdown': {
                'verified': verified,
                'pending': pending,
                'rejected': rejected
            },
            'featured_events': featured,
            'by_category': categories,
            'by_district': districts,
            'engagement': {
                'total_confirmations': EventConfirmation.objects.count(),
                'total_attendees': Attendance.objects.count()
            }
        })

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Filter events by category"""
        category = request.query_params.get('category')
        if not category:
            return Response(
                {'error': 'category parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        events = Event.objects.filter(category=category).order_by('-event_date')
        serializer = AdminEventListSerializer(events, many=True)
        return Response({
            'category': category,
            'total': events.count(),
            'events': serializer.data
        })
