from django.conf.urls import include, url
from django.views.generic import TemplateView

from linkpile.feeds import LinksFeed
from linkpile import views

urlpatterns = [
    url(r'^feed/$', LinksFeed()),
    url(r'^random/$', views.random, name='linkpile-random'),
    url(r'^export/$', views.export, name='linkpile-export'),
    url(r'^new/$', views.new, name='linkpile-new'),
    url(r'^link/(?P<link_id>\d+)/edit/$', views.edit, name='linkpile-edit'),
    url(r'^link/(?P<link_id>\d+)/$', views.detail, name='linkpile-link'),
    url(r'^(?P<tags>[\w:$&-_-+/.]+)/$', views.tags, name='linkpile-tags'),
    url(r'^$', views.index, name='linkpile-index'),
]
