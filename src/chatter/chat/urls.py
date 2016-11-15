from django.conf.urls import url

from . import views

app_name = "chat"

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^create_chatroom/$', views.create_chatroom, name="create_chatroom"),
    url(r'^(?P<chatroom_id>[0-9]+)/$', views.chatroom, name="chatroom"),
    url(r'^(?P<chatroom_id>[0-9]+)/post$', views.chatroom_post, name="chatroom_post"),
    url(r'^(?P<chatroom_id>[0-9]+)/challenge/$',
        views.chatroom_password_challenge, name="chatroom_password_challenge"),
    url(r'^register_user/$', views.register_user, name="register_user"),
]
