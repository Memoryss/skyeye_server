from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.Show.init, name='show'),
    url(r'^chart/$', views.Show.chart, name='show'),
    url(r'^searchName/$', views.Search.searchName, name="searchName"),
    url(r'^searchUser/$', views.Search.searchUser, name="searchUser"),
    url(r'^searchOpt/$', views.Search.searchOpt, name="searchOpt"),
    url(r'^searchDetailChart/$', views.Search.searchDetailChart, name="searchDetailChart"),
    url(r'^searchTimes/$', views.Search.searchTimes, name="searchTimes"),
    url(r'^searchIPTimes/$', views.Search.searchIPTimes, name="searchIPTimes"),
]