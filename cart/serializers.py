"""__author__ = 叶小永"""
from rest_framework import serializers

from cart.models import CartModel
from goods.models import SKU
from goods.serializers import SkusSerializer
from utils.errors import ParamsException


class CartSerializer(serializers.ModelSerializer):
    sku = SkusSerializer()

    def validate(self, attrs):
        sku_id = attrs['sku_id']
        count = attrs['count']
        stock = SKU.objects.get(pk=sku_id)
        if stock < count:
            res = {'code': 1030, 'msg': '库存不足'}
            raise ParamsException(res)
        return attrs

    class Meta:
        model = CartModel
        fields = '__all__'


