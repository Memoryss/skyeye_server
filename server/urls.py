from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<sessionid>[1-9]\d*|0)/operation/$', views.Session.recv_operator, name='recv_operator'),
    url(r'^(?P<sessionid>[1-9]\d*|0)/$', views.Session.recv_stop, name='recv_stop'),
    url(r'^(?P<sessionid>[1-9]\d*|0)/attachment/$', views.Session.recv_attachment, name='recv_attachment'),
    url(r'^$', views.Session.create_session, name='create_session'),
]