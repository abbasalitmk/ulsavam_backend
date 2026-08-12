import django_filters
from .models import Event

class EventFilter(django_filters.FilterSet):
    district = django_filters.CharFilter(field_name='district__slug', lookup_expr='exact')
    district_id = django_filters.NumberFilter(field_name='district__id', lookup_expr='exact')
    category = django_filters.CharFilter(field_name='category', lookup_expr='exact')
    date = django_filters.DateFilter(field_name='event_date', lookup_expr='exact')
    date_from = django_filters.DateFilter(field_name='event_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='event_date', lookup_expr='lte')
    verified_only = django_filters.BooleanFilter(method='filter_verified_only')
    is_featured = django_filters.BooleanFilter(field_name='is_featured')

    class Meta:
        model = Event
        fields = ['district', 'district_id', 'category', 'date', 'date_from', 'date_to', 'is_featured']

    def filter_verified_only(self, queryset, name, value):
        if value:
            return queryset.filter(status='verified')
        return queryset
