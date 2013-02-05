from django.conf.urls import patterns, url

from public import views

urlpatterns = patterns('',
    url(r'thanks/$', views.thanks, name='thanks'),
    url(r'^contact$', views.contact, name='contact'),
    # ex: /poll/
    url(r'^$', views.pollview, name='index'),
    # ex: /poll/5/
    url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
    # ex: /poll/5/results/
    url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
    # ex: /poll/5/vote/
    url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
)
