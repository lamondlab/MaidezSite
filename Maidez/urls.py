from django.conf.urls import url
from .views import *

urlpatterns=[
    url(r'^$', index, name="index"),
    url(r'^heartbeat/$', heartbeat, name="heartbeat"),
    url(r'^rpc/$', rpc, name="rpc"),
]
