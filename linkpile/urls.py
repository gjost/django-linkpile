from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from linkpile.feeds import LinksFeed

urlpatterns = patterns(
    '',
    url(r'^feed/$', LinksFeed()),
    url(r'^export/$', 'linkpile.views.export', name='linkpile-export'),
    url(r'^new/$', 'linkpile.views.new', name='linkpile-new'),
    url(r'^link/(?P<link_id>\d+)/edit/$', 'linkpile.views.edit', name='linkpile-edit'),
    url(r'^link/(?P<link_id>\d+)/$', 'linkpile.views.detail', name='linkpile-link'),
    url(r'^(?P<tags>[\w.-]+)/$', 'linkpile.views.tags', name='linkpile-tags'),
    url(r'^$', 'linkpile.views.index', name='linkpile-index'),
)
