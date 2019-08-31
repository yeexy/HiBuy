"""__author__ = 叶小永"""
from rest_framework.routers import SimpleRouter

from cart.views import CartView

router = SimpleRouter()

router.register('cart', CartView)

urlpatterns = [

]

urlpatterns += router.urls
