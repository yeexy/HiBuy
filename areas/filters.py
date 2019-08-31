"""__author__ = 叶小永"""
import django_filters

from areas.models import Area


class AddressFilter(django_filters.rest_framework.FilterSet):
    province_id = django_filters.CharFilter(method='filter_province')
    city_id = django_filters.CharFilter(method='filter_city')

    # 根据省份id过滤出市的信息
    def filter_province(self, queryset, name, value):
        if value:
            return queryset.filter(parent_id=value)

    # 根据市id过滤出区、县的信息
    def filter_city(self, queryset, name, value):
        if value:
            return queryset.filter(parent_id=value)
        else:
            return queryset

    class Meta:
        model = Area
        fields = '__all__'

