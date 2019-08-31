from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from cart.models import CartModel
from cart.serializers import CartSerializer
from utils.auth import UserLoginAuth


class CartView(viewsets.GenericViewSet, mixins.ListModelMixin,
               mixins.CreateModelMixin, mixins.UpdateModelMixin,
               mixins.DestroyModelMixin):
    queryset = CartModel.objects.all()
    serializer_class = CartSerializer
    authentication_classes = (UserLoginAuth,)

    # 显示购物车商品信息
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        res = {'cart': serializer.data}
        return Response(res)

    # 添加购物车
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        user = request.user
        count = request.data['count']
        sku_id = request.data['sku_id']
        CartModel.objects.create(user=user, c_num=count, sku_id=sku_id)
        res = {'count': CartModel.objects.all().count()}
        return Response(res)

    # 勾选商品
    def update(self, request, *args, **kwargs):
        good = self.get_object()
        good.is_select = request.data['selected']
        good.save()
        res = {'selected': good.is_select}
        return Response(res)

    # 购物车全选
    @action(detail=False, methods=['PUT'])
    def selection(self, request):
        queryset = self.queryset.filter(user=request.user).all()
        for good in queryset:
            good.is_select = request.data['selected']
            good.save()
        res = {'selected': request.data['selected']}
        return Response(res)

    # 增加商品数量
    @action(detail=False, methods=['PUT'])
    def add(self, request):
        queryset = self.queryset.get(pk=request.data['sku_id'])
        queryset.c_num += 1
        queryset.save()
        res = {'count': queryset.c_num}
        return Response(res)

    # 减少商品数量
    @action(detail=False, methods=['PUT'])
    def minus(self, request):
        queryset = self.queryset.get(pk=request.data['sku_id'])
        queryset.c_num -= 1
        queryset.save()
        res = {'count': queryset.c_num}
        return Response(res)

    # 用户输入商品数量
    @action(detail=False, methods=['PUT'])
    def input(self, request):
        queryset = self.queryset.get(pk=request.data['sku_id'])
        queryset.c_num = request.data['count']
        queryset.save()
        res = {'count': queryset.c_num}
        return Response(res)

    # 删除购物车商品
    def destroy(self, request, *args, **kwargs):
        good = self.get_object()
        good.delete()
        res = {'msg': '删除商品成功'}
        return Response(res)

