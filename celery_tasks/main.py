"""__author__ = 叶小永"""
from celery import Celery

import os

"""
celery_tasks中的main需要在Terminal中单独启动服务才行，
启动命令: celery -A celery_tasks.main worker -l info --pool=solo

因为一开始使用: celery -A celery_tasks.main worker -l info
然而启动服务器错误: Celery ValueError: not enough values to unpack (expected 3, got 0)
通过百度说: win10上运行celery4.x就会出现这个问题，解决办法如下,原理未知：
安装eventlet: pip install eventlet，启动命令换成：
celery -A celery_tasks.main worker -l info -P eventlet

但是celery又报错: TypeError: wrap_socket() got an unexpected keyword argument '_context'
因为requests包的requests.post发送后，传不回数据
最后改变celery启动方法不要用eventlet，加个参数--pool=solo成功运行
celery -A celery_tasks.main worker -l info --pool=solo
"""
# 为celery使用django配置文件进行配置
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo.settings'

# 创建celery应用
app = Celery('meiduo')

# 导入celery配置
app.config_from_object('celery_tasks.config')

# 自动注册celery任务，启动celery后，可以看到一个[tasks] . send_verity_email 任务
app.autodiscover_tasks(['celery_tasks.email'])

