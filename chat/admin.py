from django.contrib import admin
from .models import Room, Log


class AdminLog(admin.ModelAdmin):
    list_display = ['name', "creation_date", "edit_date"]
    list_display_links = ['name', ]


admin.site.register(
    Room,
    list_display=["id", "title", "room_log", "staff_only"],
    list_display_links=["id", "title", "room_log"],
)

admin.site.register(Log, admin_class=AdminLog)
