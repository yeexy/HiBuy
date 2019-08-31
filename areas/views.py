from rest_framework import viewsets, mixins
from rest_framework.response import Response

from areas.filters import AddressFilter
from areas.models import Area
from areas.serializers import AreaSerializer


class AreasView(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    # 过滤类
    filter_class = AddressFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # 获取所有的省份信息
        provinces = Area.objects.filter(parent=None).all()
        res = {
            'provinces': self.get_serializer(provinces, many=True).data,
            'cities': serializer.data,
            'districts': serializer.data
        }
        return Response(res)

