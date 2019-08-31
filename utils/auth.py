"""__author__ = 叶小永"""
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication

from user.models import User
from utils.errors import ParamsException


class UserLoginAuth(BaseAuthentication):

    def authenticate(self, request):
        token = request.data['token'] if request.data.get('token') else request.query_params.get('token')
        if not token:
            token = request.META.get("HTTP_AUTHORIZATION")[4:]
        if not token:
            res = {'code': 1018, 'msg': '你还未登录，请去登录'}
            raise ParamsException(res)
        user_id = cache.get(token)
        if not user_id:
            res = {'code': 1019, 'msg': '登录信息已失效，请去登录'}
            raise ParamsException(res)
        user = User.objects.get(pk=user_id)
        return user, token


