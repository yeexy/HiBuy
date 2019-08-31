from django.db import models

from goods.models import SKU
from user.models import User, Address
from utils.models import BaseModel


class OrderInfo(BaseModel):
    """
    订单信息
    """
    order = models.AutoField(null=False, primary_key=True)
    total_count = models.IntegerField(null=False, verbose_name='总数')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, verbose_name='总价')
    freight = models.DecimalField(max_digits=10, decimal_places=2, null=False, verbose_name='运费')
    pay_method = models.SmallIntegerField(null=False, verbose_name='支付方式')
    status = models.SmallIntegerField(null=False, verbose_name='状态')
    additional_commented = models.TextField(null=True, verbose_name='追加评论')
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT, verbose_name='用户id')
    address = models.ForeignKey(Address, null=True, default=None, on_delete=models.PROTECT, verbose_name='地址id')

    class Meta:
        db_table = 'tb_order_info'


class OrderGoods(BaseModel):
    """
    商品订单
    """
    count = models.IntegerField(null=False, verbose_name='数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, verbose_name='价格')
    comment = models.TextField(null=False, verbose_name='评价')
    score = models.SmallIntegerField(max_length=6, null=False, verbose_name='分数')
    is_anonymous = models.BooleanField(default=False, null=False, verbose_name='是否匿名')
    is_commented = models.BooleanField(default=False, null=False, verbose_name='是否评论')
    additional_commented = models.TextField(null=True, verbose_name='追加评论')
    order = models.ForeignKey(OrderInfo, null=False, on_delete=models.CASCADE, verbose_name='订单id')
    sku = models.ForeignKey(SKU, null=False, on_delete=models.PROTECT, verbose_name='sku')

    class Meta:
        db_table = 'tb_order_goods'

