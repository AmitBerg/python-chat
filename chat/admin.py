from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth.models import User

from .models import Room, PrivateRoom, Log


class AdminLog(admin.ModelAdmin):
    list_display = ['name', "creation_date", "edit_date"]
    list_display_links = ['name', ]


class RoomAdminForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'

    def clean(self):
        """Make sure all managers are also members."""
        members = list(self.cleaned_data['users'])
        bot = User.objects.get_or_create(first_name="Bro", last_name="Bot", username="Brobot", password="brobot",
                                         email="bro@bot.com")[0]
        if self.cleaned_data['has_bot']:
            members.append(bot)
        self.cleaned_data['users'] = members
        return self.cleaned_data


class AdminRoom(admin.ModelAdmin):
    model = Room
    form = RoomAdminForm
    list_display = ["title", "id", "_users", "staff_only", "has_bot"]
    exclude = ['room_log']

    def _users(self, obj):
        return "\n".join([p.username for p in obj.users.all()])


class PrivateRoomAdminForm(ModelForm):
    class Meta:
        model = PrivateRoom
        exclude = ['room_log']

    def clean(self):
        """Make sure all managers are also members."""
        members = list(self.cleaned_data['users'])
        members.append(self.cleaned_data['owner'])
        if self.cleaned_data['has_bot']:
            bot = User.objects.get_or_create(first_name="Bro", last_name="Bot", username="Brobot", password="brobot",
                                             email="bro@bot.com")[0]
            members.append(bot)
        self.cleaned_data['users'] = members
        return self.cleaned_data


class AdminPrivateRoom(admin.ModelAdmin):
    model = PrivateRoom
    form = PrivateRoomAdminForm
    fields = ["title", "owner", "users", "staff_only", "has_bot"]
    list_display = ["title", "id", "owner", "_users", "staff_only", "has_bot"]

    def _users(self, obj):
        return "\n".join([p.username for p in obj.users.all()])


admin.site.register(Room, admin_class=AdminRoom)
admin.site.register(Log, admin_class=AdminLog)
admin.site.register(PrivateRoom, admin_class=AdminPrivateRoom)
