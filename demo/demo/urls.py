from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
    url(r'^wechat/', 'echo.views.wechat'),
    url(r'^auth_event/', 'echo.views.auth_event'),
    url(r'^component_access_token/$', 'echo.views.component_access_token_api'),
    url(r'^pre_auth_code/$', 'echo.views.pre_auth_code_api'),
    url(r'^authorize/$', 'echo.views.authorize'),
    url(r'^save_authorization_info/$', 'echo.views.save_authorization_info', name='save_authorization_info'),
)
