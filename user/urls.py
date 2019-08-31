"""__author__ = 叶小永"""
from django.urls import path
from rest_framework.routers import SimpleRouter

from user.views import UserView, username, mobiles, AddressesView

router = SimpleRouter()

router.register('auth', UserView)
router.register('addresses', AddressesView)

urlpatterns = [
    path('username/', username),
    path('mobiles/', mobiles)
]

urlpatterns += router.urls
