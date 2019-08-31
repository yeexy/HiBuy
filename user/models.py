from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer, BadData

from areas.models import Area
from meiduo import settings
from utils.models import BaseModel


class User(models.Model):
    username = models.CharField(max_length=32, unique=True)  # 名称
    password = models.CharField(max_length=256)  # 密码
    email = models.CharField(max_length=64, unique=True, null=True)  # 邮箱
    # False 代表女
    sex = models.BooleanField(default=False)  # 性别
    icon = models.ImageField(upload_to='icons')  # 头像
    is_delete = models.BooleanField(default=False)  # 是否删除
    # 添加手机号字段
    mobile = models.CharField(max_length=11, verbose_name="手机号")
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    # 添加默认收货地址
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'  # 表名

    def generate_verify_email_url(self):
        # 过期时间600秒
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=600)
        # 加入传输的数据
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data).decode()
        # verify_url = 'http://127.0.0.1:8000/success_verify_email.html?token=' + token

        verify_url = 'http://127.0.0.1:8020/front_end_pc/success_verify_email.html?token=' + token
        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=600)
        # 解析加密的数据,loads()
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            email = data.get('email')
            user_id = data.get('user_id')
            user = User.objects.filter(id=user_id, email=email).first()
            if user:
                return user
            else:
                return None


class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        # 默认是按照id排序,可以指定为按照修改时间降序排列
        ordering = ['-update_time']

