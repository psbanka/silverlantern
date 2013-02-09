from django.conf.urls import patterns, url, include
from public import views
from django.contrib.auth.views import login

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^login/$', login, {'template_name': 'auth.html'}),
    url(r'^logout/$', views.logout_view),
    url(r'^accounts/profile/$', views.profile, name="profile"),
    url(r'^oauth2callback/$', views.oauth2callback, name="oauth2callback"),
    url(r'^polls/', include('public.urls', namespace='polls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
