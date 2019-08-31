"""__author__ = 叶小永"""
from rest_framework import serializers

from goods.models import GoodsCategory, SKU, SKUSpecification,\
    SpecificationOption, GoodsSpecification


class GoodsCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class SkusSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = '__all__'


class SpecOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpecificationOption
        fields = ['value', 'spec', 'id']


class GoodsSpecSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsSpecification
        fields = ['name', 'goods', 'id']


class DetailSerializer(serializers.ModelSerializer):

    # 重构data结构
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['name'] = GoodsSpecSerializer(instance.spec).data['name']
        detail_specs = SpecificationOption.objects.filter(spec=instance.spec).all()
        result = []
        for spec in detail_specs:
            result.append(SpecOptionSerializer(spec).data)
        data['options'] = result
        return data

    class Meta:
        model = SKUSpecification
        fields = '__all__'

