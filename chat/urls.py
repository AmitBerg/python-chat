from django.conf.urls import url
from . import views

app_name = "chat"

urlpatterns = [
    url(r'^room/(?P<pk>[0-9]+)$', views.ChatRoomDetailView.as_view(), name='single_room'),
    url(r'statistics/', views.StatisticsView.as_view(), name="statistics"),
]
