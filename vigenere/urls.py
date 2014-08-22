# ~*~ coding: utf-8 ~*~
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, url


urlpatterns = patterns('',
                       url(r'^$', 'project.views.encryption_view'),
                       url(r'^encryption_final/$', 'project.views.encryption_final_view'),
                       url(r'^decryption/$', 'project.views.decryption_view'),
                       url(r'^decryption_final/$', 'project.views.decryption_final_view'),
                       url(r'^markov/$', 'project.views.markov_chains_view'),
                       url(r'^markov_final/$', 'project.views.markov_chains_final_view'),
                       )

urlpatterns += staticfiles_urlpatterns()