"""__author__ = 叶小永"""
from rest_framework import serializers

from areas.models import Area
from user.models import Address


# 地区序列化类
class AreaSerializer(serializers.ModelSerializer):
    addresses = Address.objects.all()

    class Meta:
        model = Area
        fields = '__all__'

