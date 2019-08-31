from rest_framework import viewsets, mixins
from rest_framework.decorators import action

from rest_framework.response import Response

from goods.filters import GoodsFilter
from goods.models import GoodsCategory, SKU, SKUSpecification
from goods.serializers import GoodsCategorySerializer, SkusSerializer, \
    DetailSerializer


class CategoryView(viewsets.GenericViewSet, mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):
    queryset = SKU.objects.all()
    serializer_class = GoodsCategorySerializer
    filter_class = GoodsFilter

    # 获取分类信息
    def retrieve(self, request, *args, **kwargs):
        category = GoodsCategory.objects.get(pk=kwargs['pk'])
        res = {
            'cat2': self.get_serializer(category).data,
            'cat1': {'category': self.get_serializer(category.parent).data},
            'cat0': self.get_serializer(category.parent.parent).data
        }
        return Response(res)

    # 获取分类下所有商品信息
    @action(detail=True, serializer_class=SkusSerializer, methods=['GET'])
    def skus(self, request, *args, **kwargs):
        category = GoodsCategory.objects.get(pk=kwargs['pk'])
        skus = SKU.objects.filter(category=category).all()
        # 调用过滤类，按默认、价格、人气来过滤
        queryset = self.filter_queryset(self.queryset.filter(category=category))
        serializer = self.get_serializer(queryset, many=True)
        res = {
            'count': skus.count(),
            'results': serializer.data
        }
        return Response(res)


# 获取商品详情
class DetailView(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = SKUSpecification.objects.all()
    serializer_class = DetailSerializer

    def retrieve(self, request, *args, **kwargs):
        sku = SKU.objects.get(pk=kwargs['pk'])
        queryset = self.queryset.filter(sku_id=kwargs['pk']).all()
        res = {
            'sku': SkusSerializer(sku).data,
            'specs': self.get_serializer(queryset, many=True).data
        }
        return Response(res)

