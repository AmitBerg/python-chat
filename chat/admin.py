from django.contrib import admin
from .models import Room, PrivateRoom, Log


class AdminLog(admin.ModelAdmin):
    list_display = ['name', "creation_date", "edit_date"]
    list_display_links = ['name', ]


class AdminRoom(admin.ModelAdmin):
    fields = ("title", "room_log", "staff_only")
    list_display = ["title", "id", "room_log", "staff_only"]


class AdminPrivateRoom(admin.ModelAdmin):
    fields = ("title", "owner", "users", "room_log", "staff_only")
    list_display = ["title", "id", "room_log", "staff_only"]


admin.site.register(Room, admin_class=AdminRoom)
admin.site.register(Log, admin_class=AdminLog)
admin.site.register(PrivateRoom, admin_class=AdminPrivateRoom)
