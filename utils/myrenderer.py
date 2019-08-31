"""__author__ = 叶小永"""
from rest_framework.renderers import JSONRenderer


class MyJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data:
            if isinstance(data, dict):
                code = data.pop('code', 200)
                msg = data.pop('msg', '请求成功')
                result = data.pop('data', data)
            else:
                code = 200
                msg = '请求成功'
                result = data
        else:
            code = 200
            msg = '请求成功'
            result = {}

        # 修改响应状态码，让前端提示错误信息
        renderer_context['response'].status_code = 200

        res = {
            'code': code,
            'msg': msg,
            'data': result
        }
        return super().render(res)
