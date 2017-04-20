from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.Show.init, name='show'),
    url(r'^searchName/$', views.Search.searchName, name="searchName"),
    url(r'^searchUser/$', views.Search.searchUser, name="searchUser"),
    url(r'^searchOpt/$', views.Search.searchOpt, name="searchOpt"),
]