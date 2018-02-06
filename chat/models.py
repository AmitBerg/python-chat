from django.core.files.base import ContentFile, File
from django.core.files.storage import FileSystemStorage
from django.db import models
from channels import Group
import json
import os

from .settings import MSG_TYPE_MESSAGE


class Room(models.Model):
    """
    A room for people to chat in.
    """

    # Room title
    title = models.CharField(max_length=255)

    # If only "staff" users are allowed (is_staff on django's User)
    staff_only = models.BooleanField(default=False)

    room_log = models.ForeignKey("Log", on_delete=models.CASCADE, blank=True, null=True, default=None)

    def str(self):
        return self.title

    @property
    def websocket_group(self):
        """
        Returns the Channels Group that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return Group("room-%s" % self.id)

    def send_message(self, message, user, msg_type=MSG_TYPE_MESSAGE):
        """
        Called to send a message to the room on behalf of a user.
        """
        final_msg = {'room': str(self.id), 'message': message, 'username': user.username, 'msg_type': msg_type}

        # Send out the message to everyone in the room
        self.websocket_group.send(
            {"text": json.dumps(final_msg)}
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.room_log = Log.objects.create(name=join_by_dash(self.title))
        return super(Room, self).save(*args, **kwargs)


def join_by_dash(name):
    """
    if the name 'Room 1' is given, the output would be 'Room-1'
    """
    return "-".join(name.split())


LOG_PATH = "media/chat/logs/"


class Log(models.Model):
    """
    A log to save conversations
    """
    fs = FileSystemStorage(location=LOG_PATH)

    name = models.CharField(max_length=256)
    creation_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    log_file = models.FileField(storage=fs, blank=True, null=True)

    def __str__(self):
        # TODO rework this function, maybe format the time string differently
        return "Log name: " + self.name + " Created at: " + str(
            self.creation_date.strftime("%d-%m-%Y %H:%M:%S")) + " Last changed at: " + str(
            self.edit_date.strftime("%d-%m-%Y %H:%M:%S"))

    def save(self, *args, **kwargs):
        if not self.pk:
            if not os.path.exists(LOG_PATH):
                os.makedirs(LOG_PATH)
                self.log_file.save(self.name + '.csv', ContentFile('time room user message\n'))
                return
            elif not os.path.isfile(LOG_PATH + self.name + '.csv'):
                self.log_file.save(self.name + '.csv', ContentFile('time room user message\n'))
                return
        return super(Log, self).save(*args, **kwargs)
