from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.ChatRoomsListView.as_view(), name='rooms'),
    url(r'^room/(?P<pk>[0-9]+)$', views.ChatRoomDetailView.as_view(), name='single_room'),
]
