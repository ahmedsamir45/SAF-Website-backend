import django_filters
from .models import Program

class ProgramFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    cost_min = django_filters.NumberFilter(field_name='cost', lookup_expr='gte')
    cost_max = django_filters.NumberFilter(field_name='cost', lookup_expr='lte')
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    
    class Meta:
        model = Program
        fields = {
            'type': ['exact'],
            'category': ['exact'],
            'audience': ['exact'],
            'kind': ['exact'],
            'target_academic': ['exact'],
        }