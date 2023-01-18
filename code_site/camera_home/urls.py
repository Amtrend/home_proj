from django.urls import path
from .views import *
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', login_page, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', main_page, name='home'),
    path('livecams_feed/', livecams_feed_page, name='livecams_feed'),
    path('cams_archive/', cams_archive_page, name='cams_archive'),
    path('settings/', settings_page, name='settings'),
    path('archive/<int:pk>/', streaming_video, name='stream_video'),
    path('download/<int:pk>/', download_video, name='download_video'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('favicon.ico', RedirectView.as_view(url='static/img/favicon.ico'), name='favicon'),
]
