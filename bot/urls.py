from django.conf.urls import url

from .views import BotView

app_name = "bot"

urlpatterns = [
    # my lovely bot view
    url(r'bot/$', BotView.as_view(), name="bot"),
]