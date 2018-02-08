from django.db import models
from channels import Group
import json

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


BASE_CONVERSATION = '{ "conversation" : [] }'

example = '{"conv": [{"time": "1", "user": "me", "msg": "some message"}, ' \
          '{"time": "2", "user": "other", "msg": "some other message"}]}'


class Log(models.Model):
    """
    A log to save conversations
    """
    name = models.CharField(max_length=256)
    creation_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    conversation = models.TextField(default=BASE_CONVERSATION, blank=True, null=True)

    def __str__(self):
        # TODO rework this function, maybe format the time string differently
        return "Log name: " + self.name + " Created at: " + str(
            self.creation_date.strftime("%d-%m-%Y %H:%M:%S")) + " Last changed at: " + str(
            self.edit_date.strftime("%d-%m-%Y %H:%M:%S"))

    def read(self):
        return json.loads(self.conversation)

    @staticmethod
    def write(conversation):
        return json.dumps(conversation)

    def add_message(self, message):
        # message must be a dict of time, user, and the actual message
        if type(message) != dict:
            return
        conversation = self.read()
        conversation['conversation'].append(message)
        self.conversation = self.write(conversation)
        self.save()

    def prettify_conversation(self):
        base_message = '<p><span style="color: blue;">{} </span>{}: {}</p>'
        conversation = ""
        for msg in self.read()['conversation']:
            conversation += (base_message.format(msg['time'], msg['user'], msg['msg']))
        return conversation, len(self.read()['conversation'])
