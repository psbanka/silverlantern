from django.conf.urls import patterns, url, include
from main import views
from main import rest
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
    url(r'^fetch_my_mail/$', views.fetch_my_mail, name="fetch_my_mail"),
    url(r'^study/$', views.study, name="study"),
    url(r'^gallery/$', views.gallery, name="gallery"),
    url(r'^remove/(?P<word_to_remove>.*)$', views.remove, name="remove"),
    url(r'^def/(?P<word_to_lookup>.*)$', views.definition, name="definition"),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^json/gallery_words/(?P<category>.*)$',
        rest.gallery_words, name="gallery_words"),
    url(r'^json/gallery_categories/$',
        rest.gallery_categories, name="gallery_words"),
    url(r'^contact$', views.contact, name='contact'),
    url(r'^test/e2e$', views.e2e, name='e2e'),
)
