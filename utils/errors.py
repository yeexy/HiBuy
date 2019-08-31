"""__author__ = 叶小永"""
from rest_framework.exceptions import APIException


# 抛出错误信息
class ParamsException(APIException):

    def __init__(self, msg):
        self.detail = msg

