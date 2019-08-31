"""__author__ = 叶小永"""
import re
import uuid

from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import cache
from rest_framework import serializers

from areas.serializers import AreaSerializer
from user.models import User, Address
from utils.errors import ParamsException
from celery_tasks.email import tasks as email_tasks


# 用户序列化类
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


# 用户注册序列化类
class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=20, min_length=5,
                                     error_messages={'required': '用户名不能为空',
                                                     'max_length': '用户名不能超过20位',
                                                     'min_length': '用户名不能少于5位'})
    password = serializers.CharField(required=True, max_length=20, min_length=8,
                                     error_messages={'required': '密码不能为空',
                                                     'max_length': '密码不能超过20位',
                                                     'min_length': '密码不能少于8位'})
    password2 = serializers.CharField(required=True, max_length=20, min_length=8,
                                      error_messages={'required': '密码不能为空',
                                                      'max_length': '密码不能超过20位',
                                                      'min_length': '密码不能少于8位'})
    mobile = serializers.CharField(required=True, max_length=11, min_length=11,
                                   error_messages={'required': '手机号不能为空',
                                                   'max_length': '手机号不能超过11位',
                                                   'min_length': '手机号不能少于11位'})
    allow = serializers.BooleanField(required=True, error_messages={'required': '未同意用户协议'})

    # 注册信息校验
    def validate(self, attrs):
        # 验证用户名
        username = attrs['username']
        if User.objects.filter(username=username).exists():
            res = {'code': 1007, 'msg': '用户名已存在'}
            raise ParamsException(res)
        # 验证两次密码输入是否一致
        pwd1 = attrs['password']
        pwd2 = attrs['password2']
        if pwd1 != pwd2:
            res = {'code': 1008, 'msg': '两次密码输入不一致'}
            raise ParamsException(res)
        # 验证手机号是否已注册
        phone = attrs['mobile']
        if User.objects.filter(mobile=phone).exists():
            res = {'code': 1009, 'msg': '手机号已注册'}
            raise ParamsException(res)
        # 验证短信验证码是否正确

        # 验证是否同意用户协议
        if not attrs['allow']:
            res = {'code': 1011, 'msg': '未同意用户使用协议'}
            raise ParamsException(res)
        return attrs

    # 注册成功重构创建方法
    def create(self, validated_data):
        username = validated_data['username']
        password = make_password(validated_data['password'])
        mobile = validated_data['mobile']
        user = User.objects.create(username=username,
                                   password=password,
                                   mobile=mobile)
        return user

    # 生成一个token并存到redis
    def user_token(self, data):
        token = uuid.uuid4().hex
        user = User.objects.filter(username=data['username']).first()
        cache.set(token, user.id, timeout=30000)
        return token

    class Meta:
        model = User
        fields = '__all__'


# 用户登录序列化类
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=20, min_length=5,
                                     error_messages={'required': '用户名不能为空',
                                                     'max_length': '用户名不能超过20位',
                                                     'min_length': '用户名不能少于5位'})
    password = serializers.CharField(required=True, max_length=20, min_length=8,
                                     error_messages={'required': '密码不能为空',
                                                     'max_length': '密码不能超过20位',
                                                     'min_length': '密码不能少于8位'})

    # 用户登录信息校验
    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']
        user = User.objects.filter(username=username).first()
        if not user:
            res = {'code': 1014, 'msg': '用户名不存在，请去注册'}
            raise ParamsException(res)
        if not check_password(password, user.password):
            res = {'code': 1015, 'msg': '用户名或密码不正确'}
            raise ParamsException(res)
        return attrs

    # 生成一个token并存储到redis
    def login_token(self, data):
        token = uuid.uuid4().hex
        user = User.objects.filter(username=data['username']).first()
        cache.set(token, user.id, timeout=30000)
        return token

    class Meta:
        model = User
        fields = '__all__'


# 用户邮件序列化类
class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True,
                                   error_messages={'required': '邮件不能为空'})

    # 邮箱校验
    def validate(self, attrs):
        # token = attrs['token']
        # if cache.get(token):
        #     res = {'code': 1017, 'msg': '登录已失效，请重新登录'}
        #     raise ParamsException(res)
        email = attrs['email']
        if not re.fullmatch(r'[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}', email):
            res = {'code': 1017, 'msg': '邮箱格式不正确'}
            raise ParamsException(res)
        return attrs

    def update(self, instance, validated_data):
        # 保存邮箱
        instance.email = validated_data['email']
        instance.save()

        # 在保存数据的返回之前，生成邮箱的激活连接
        verity_url = instance.generate_verify_email_url()

        # 发送激活邮件
        # 需要先导入from celery_tasks.email import tasks as email_tasks
        email_tasks.send_verity_email.delay(instance.email, verity_url)
        return instance

    class Meta:
        model = User
        fields = '__all__'


# 用户地址序列化类
class AddressesSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    title = serializers.CharField(required=True, max_length=20,
                                  error_messages={
                                      'required': '标题必填',
                                      'max_length': '标题不能超过20个字符'
                                  })
    receiver = serializers.CharField(required=True, max_length=20,
                                     error_messages={
                                         'required': '收货人必填',
                                         'max_length': '收货人不能超过20个字符'
                                     })
    # 外键的序列化
    province = AreaSerializer(required=False)
    city = AreaSerializer(required=False)
    district = AreaSerializer(required=False)

    place = serializers.CharField(required=True, max_length=50,
                                  error_messages={
                                      'required': '详细地址必填',
                                      'max_length': '详细地址不能超过50个字符'
                                  })
    mobile = serializers.CharField(required=True, max_length=11, min_length=11,
                                   error_messages={
                                       'required': '手机必填',
                                       'max_length': '手机号不能超过11个字符',
                                       'min_length': '手机号不能少于11个字符'
                                   })
    tel = serializers.CharField(allow_blank=True)
    email = serializers.CharField(allow_blank=True)

    def validate(self, attrs):
        # 校验手机号格式
        mobile = attrs['mobile']
        if not re.fullmatch(r'1[345789]\d{9}', mobile):
            res = {'code': 1022, 'msg': '手机号格式不正确'}
            raise ParamsException(res)
        # 如果填了固定电话，校验电话格式
        tel = attrs['tel']
        if tel:
            if not re.fullmatch(r'(0[0-9]{2,3}/-)?([2-9][0-9]{6,7})+(/-[0-9]{1,4})?', tel):
                res = {'code': 1023, 'msg': '固定电话格式不正确'}
                raise ParamsException(res)
        # 如果填了邮箱，校验邮箱格式
        email = attrs['email']
        if email:
            if not re.fullmatch(r'[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}', email):
                res = {'code': 1024, 'msg': '邮箱格式不正确'}
                raise ParamsException(res)
        return attrs

    class Meta:
        model = Address
        fields = '__all__'


class TitleSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, max_length=20,
                                  error_messages={
                                      'required': '收货地址标题必填',
                                      'max_length': '标题不能超过20个字符'
                                  })

    class Meta:
        model = Address
        fields = ['title']

