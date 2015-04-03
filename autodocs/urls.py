from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url('^$',
        views.doc_index,
        name='django-autodocs-docroot'
    ),
    url('^bookmarklets/$',
        views.bookmarklets,
        name='django-autodocs-bookmarklets'
    ),
    url('^tags/$',
        views.template_tag_index,
        name='django-autodocs-tags'
    ),
    url('^filters/$',
        views.template_filter_index,
        name='django-autodocs-filters'
    ),
    url('^views/$',
        views.view_index,
        name='django-autodocs-views-index'
    ),

    url('^views/(?P<view>[^/]+)/$',
        views.view_detail,
        name='django-autodocs-views-detail'
    ),
    url('^views/(?P<view>.*)/(?P<viewclass>.*)\.txt$',
        views.view_class_detail,
        name='django-autodocs-views-detail-rst'
    ),
    url('^urls/$',
        views.url_index,
        name='django-autodocs-urls-index'
    ),
    url('^urls/(?P<url>[^/]+)/$',
        views.url_detail,
        name='django-autodocs-urls-detail'
    ),
    url('^models/$',
        views.model_index,
        name='django-autodocs-models-index'
    ),
    url('^models/(?P<app_label>[^\.]+)\.(?P<model_name>[^/]+)/$',
        views.model_detail,
        name='django-autodocs-models-detail'
    ),
    url('^templates/(?P<template>.*)/$',
        views.template_detail,
        name='django-autodocs-templates'
    ),
)
