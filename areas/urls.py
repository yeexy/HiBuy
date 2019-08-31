"""__author__ = 叶小永"""
from rest_framework.routers import SimpleRouter

from areas.views import AreasView

router = SimpleRouter()

router.register('areas', AreasView)

urlpatterns = [

]

urlpatterns += router.urls

