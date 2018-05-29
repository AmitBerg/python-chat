from django.contrib import admin

from .models import Response


class ResponseAdmin(admin.ModelAdmin):
    fields = ("type", "text")
    list_display = ['type', "text", "date"]
    list_display_links = ["type", "text"]


admin.site.register(Response, ResponseAdmin)
