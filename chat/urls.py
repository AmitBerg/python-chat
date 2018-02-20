from django.conf.urls import url
from . import views

app_name = "chat"

urlpatterns = [
    url(r'^room/(?P<pk>[0-9]+)$', views.ChatRoomDetailView.as_view(), name='single_room'),
    url(r'^private_room/(?P<pk>[0-9]+)$', views.PrivateRoomView.as_view(), name='single_private_room'),
    url(r'^private_room/create$', views.CreatePrivateRoom.as_view(), name='create_private_room'),
    url(r'^private_room/update/(?P<pk>[0-9]+)$', views.UpdatePrivateRoom.as_view(), name='update_private_room'),
    url(r'^statistics/$', views.StatisticsView.as_view(), name="statistics"),
    url(r'^statistics/api$', views.StatisticsApiView.as_view(), name="statistics_api"),
]
