import re

from django.core.cache import cache
from rest_framework import viewsets, mixins
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from user.models import User, Address
from user.serializers import UserSerializer, UserRegisterSerializer, \
    UserLoginSerializer, EmailSerializer, AddressesSerializer, TitleSerializer
from utils.auth import UserLoginAuth
from utils.errors import ParamsException


# 验证用户名是否有效
@api_view(http_method_names=['GET'])
def username(request):
    name = request.GET.get('username')
    if len(name) < 5:
        res = {'code': 1001, 'msg': '用户名不能少于5位'}
        raise ParamsException(res)
    elif len(name) > 20:
        res = {'code': 1002, 'msg': '用户名不能超过20位'}
        raise ParamsException(res)
    user = User.objects.filter(username=name)
    if user:
        res = {'code': 1003, 'msg': '用户名已存在', 'count': user.count()}
        return Response(res)
    else:
        res = {'msg': '用户名有效'}
        return Response(res)


# 验证手机号是否有效
@api_view(http_method_names=['GET'])
def mobiles(request):
    num = request.GET.get('mobile')
    if len(num) != 11:
        res = {'code': 1004, 'msg': '手机号长度不正确'}
        raise ParamsException(res)
    elif not re.fullmatch(r'1[345789]\d{9}', num):
        res = {'code': 1005, 'msg': '手机号格式不正确'}
        raise ParamsException(res)
    phone = User.objects.filter(mobile=num)
    if phone:
        res = {'code': 1006, 'msg': '手机号已注册', 'count': phone.count()}
        return Response(res)
    else:
        res = {'msg': '手机号有效'}
        return Response(res)


class UserView(viewsets.GenericViewSet, mixins.ListModelMixin,
               mixins.UpdateModelMixin, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        token = request.query_params.get('token')
        user_id = cache.get(token)
        user = User.objects.filter(pk=user_id).first()

        res = {'data': self.get_serializer(user).data}
        return Response(res)

    # 注册功能
    @action(detail=False, serializer_class=UserRegisterSerializer, methods=['POST'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        result = serializer.is_valid(raise_exception=False)
        if not result:
            errors = serializer.errors
            res = {
                'code': 1012,
                'msg': '字段校验失败',
                'data': errors
            }
            raise ParamsException(res)

        user = serializer.save()
        token = serializer.user_token(serializer.validated_data)
        res = {
            'token': token,
            'username': user.username,
            'id': user.id
        }
        return Response(res)

    # 登录功能
    @action(detail=False, serializer_class=UserLoginSerializer, methods=['POST'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        result = serializer.is_valid(raise_exception=False)
        if not result:
            errors = serializer.errors
            res = {
                'code': 1013,
                'msg': '字段校验失败',
                'data': errors
            }
            raise ParamsException(res)
        token = serializer.login_token(serializer.data)
        user = User.objects.filter(username=request.data['username']).first()
        res = {
            'token': token,
            'user_id': user.id,
            'username': user.username
        }
        return Response(res)

    # 邮箱验证功能
    @action(detail=False, serializer_class=EmailSerializer, methods=['PATCH'],
            authentication_classes=(UserLoginAuth,))
    def emails(self, request):
        serializer = self.get_serializer(data=request.data)
        result = serializer.is_valid(raise_exception=False)
        if not result:
            errors = serializer.errors
            res = {
                'code': 1016,
                'msg': '邮箱检验失败',
                'data': errors
            }
            raise ParamsException(res)
        token = request.data['token']
        user_id = cache.get(token)
        user = User.objects.get(pk=user_id)
        # update方法用于保存邮箱
        serializer.update(user, serializer.data)
        res = {'msg': '邮件发送成功'}
        return Response(res)

    # 用户点击邮件中的激活链接的校验方法
    @action(detail=False, methods=['GET'])
    def verification(self, request):
        # 获取激活链接中的token值用于校验
        token = request.query_params.get('token')
        if not token:
            res = {'code': 1020, 'msg': '你还未登录，请去登录'}
            raise ParamsException(res)
        user = User.check_verify_email_token(token)
        if not user:
            res = {'code': 1021, 'msg': '登录信息失效，请重新登录'}
            raise ParamsException(res)

        # 校验成功修改数据库邮件激活状态字段为True
        user.email_active = True
        user.save()
        res = {'msg': '邮箱验证成功'}
        return Response(res)


class AddressesView(viewsets.GenericViewSet, mixins.ListModelMixin,
                    mixins.CreateModelMixin, mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin):
    queryset = Address.objects.all()
    serializer_class = AddressesSerializer
    authentication_classes = (UserLoginAuth,)

    # 展示用户所有收货地址
    def list(self, request, *args, **kwargs):
        token = self.request.query_params['token']
        user_id = cache.get(token)
        addresses = Address.objects.filter(user_id=user_id).all()
        user = User.objects.get(pk=user_id)
        res = {
            'addresses': self.get_serializer(addresses, many=True).data,
            'default_address': UserSerializer(user).data['default_address']
        }
        return Response(res)

    # 创建新收货地址
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        result = serializer.is_valid(raise_exception=False)
        if not result:
            errors = serializer.errors
            res = {
                'code': 1025,
                'msg': '字段校验失败',
                'data': errors
            }
            raise ParamsException(res)
        user = self.request.user
        limit = Address.objects.filter(user=user).all().count()
        # 前端设置的限制创建地址数量
        if limit >= 10:
            res = {'code': 1026, 'msg': '最多可创建10个收货地址'}
            return Response(res)
        # 保存地址
        address = Address.objects.create(title=self.request.data['receiver'],
                                         receiver=self.request.data['receiver'],
                                         place=self.request.data['place'],
                                         mobile=self.request.data['mobile'],
                                         tel=self.request.data.get('tel'),
                                         email=self.request.data.get('email'),
                                         province_id=self.request.data.get('province_id'),
                                         city_id=self.request.data.get('city_id'),
                                         district_id=self.request.data.get('district_id'),
                                         user=user)

        res = {'msg': '添加地址成功', 'data': self.get_serializer(address).data}
        return Response(res)

    # 编辑地址并保存
    def update(self, request, *args, **kwargs):
        address = self.get_object()
        serializer = self.get_serializer(address, data=request.data)
        serializer.is_valid(raise_exception=False)
        address.title = self.request.data['receiver']
        address.receiver = self.request.data['receiver']
        address.place = self.request.data['place']
        address.mobile = self.request.data['mobile']
        address.tel = self.request.data.get('tel')
        address.email = self.request.data.get('email')
        address.province_id = self.request.data.get('province_id')
        address.city_id = self.request.data.get('city_id')
        address.district_id = self.request.data.get('district_id')
        address.user = address.user
        address.save()
        res = {'msg': '收货地址修改成功', 'data': serializer.data}
        return Response(res)

    # 设置默认地址
    @action(detail=False, methods=['PUT'])
    def status(self, request):
        token = request.data['token']
        user_id = cache.get(token)
        address_id = request.query_params['default_address_id']
        address = Address.objects.filter(user=user_id).all()
        if address:
            User.objects.filter(pk=user_id).update(default_address=address_id)
        else:
            res = {'code': 1027, 'msg': '你还没有收货地址，请先添加地址'}
            raise ParamsException(res)
        res = {'msg': '默认地址设置成功'}
        return Response(res)

    # 设置并保存标题
    @action(detail=False, serializer_class=TitleSerializer, methods=['PUT'])
    def title(self, request):
        token = request.data['token']
        user_id = cache.get(token)
        address_id = request.query_params['title_address_id']
        title = request.data['title']
        Address.objects.filter(user_id=user_id, pk=address_id).update(title=title)
        res = {'msg': '标题修改成功'}
        return Response(res)

    # 删除收货地址
    def destroy(self, request, *args, **kwargs):
        address = self.get_object()
        address.delete()
        res = {'msg': '删除地址成功'}
        return Response(res)

