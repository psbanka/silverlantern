from django.conf.urls import patterns, url

from public import views

urlpatterns = patterns(
    '',
    url(r'^contact$', views.contact, name='contact'),
)
