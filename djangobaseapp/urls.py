from django.conf.urls import url, include
from django.conf.urls import (handler400, handler403, handler404, handler500)
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

app_name = 'HLX Studios Template'
urlpatterns = [
        url(r'^register/?$', views.register_user, name='register_user'),
        url(r'^login/?$', views.user_login, name = 'user_login'),
        url(r'^/?$', views.user_login, name = 'user_login'),
        url(r'^logout/?', views.user_logout, name='user_logout'),
        url(r'^inactive/?$', views.inactive, name = 'inactive'),
        url(r'^reset/?$', views.reset, name = 'reset'),
        url(r'^requestreset/?$', views.requestreset, name = 'requestreset'),

        url(r'^account_dashboard/?$', views.account_dashboard, name = 'account_dashboard'),
        url(r'^account_invoices/?$', views.account_invoices, name = 'account_invoices'),
        url(r'^account_settings/?$', views.account_settings, name = 'account_settings'),
        
        url(r'^main_subpage_1/?$', views.main_subpage_1, name = 'main_subpage_1'),
        url(r'^main_subpage_2/?$', views.main_subpage_2, name = 'main_subpage_2'),
        url(r'^main_subpage_3/?$', views.main_subpage_3, name = 'main_subpage_3'),

        url(r'^tool_asin/?$', views.tool_asin_view, name = 'tool_asin'),

        url(r'content/$', views.content, name='content'),

        url(r'^$', views.error_404, name='error_404'),
        url(r'.+?', views.error_404, name='error_404'),
    ]
handler404 = 'djangobaseapp.views.page_not_found'
