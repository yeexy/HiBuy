"""__author__ = 叶小永"""
from rest_framework.routers import SimpleRouter

from goods.views import CategoryView, DetailView

router = SimpleRouter()

router.register('categories', CategoryView)
router.register('sku', DetailView)

urlpatterns = [

]

urlpatterns += router.urls
