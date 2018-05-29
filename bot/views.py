from django.views.generic import TemplateView


class BotView(TemplateView):
    template_name = "bot/bot.html"
