"""__author__ = 叶小永"""
import django_filters

from goods.models import SKU


# 商品的过滤类
class GoodsFilter(django_filters.rest_framework.FilterSet):
    ordering = django_filters.CharFilter(method='filter_goods')

    def filter_goods(self, queryset, name, value):
        if value == '-create_time':
            return queryset.order_by('-create_time')
        if value == 'price':
            return queryset.order_by('-price')
        if value == 'sales':
            return queryset.order_by('-sales')

    class Meta:
        model = SKU
        fields = '__all__'
