from django.db import models
from django.contrib.auth.models import User
from channels import Group
import json

from django_currentuser.middleware import get_current_authenticated_user

from .settings import MSG_TYPE_MESSAGE


class RoomManger(models.Manager):

    def exclude_private(self):
        rooms = PrivateRoom.objects.all()
        pks = [room.pk for room in rooms]
        return self.exclude(id__in=pks)

    def get_rooms_with_data(self):
        return self.exclude(room_log__conversation=BASE_CONVERSATION)


class PrivateRoomManger(models.Manager):

    def my_private_rooms(self, user):
        return self.filter(users=user)


class Room(models.Model):
    """
    A room for people to chat in.
    """

    # Room title
    title = models.CharField(max_length=255, unique=True)

    # If only "staff" users are allowed (is_staff on django's User)
    staff_only = models.BooleanField(default=False)

    users = models.ManyToManyField(User, related_name='users', blank=True)

    room_log = models.ForeignKey("Log", on_delete=models.CASCADE, blank=True, null=True, default=None)

    has_bot = models.BooleanField(default=False)

    objects = RoomManger()

    def __str__(self):
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

    def delete(self, using=None, keep_parents=False):
        if self.pk:
            self.room_log.delete()
        return super(Room, self).delete()


class PrivateRoom(Room):
    """
    private room
    """
    # this is an awesome thing!
    owner = models.ForeignKey(User, default=get_current_authenticated_user, on_delete=models.CASCADE)

    objects = PrivateRoomManger()

    def delete(self, using=None, keep_parents=False):
        if self.pk:
            self.room_log.delete()
        return super(Room, self).delete()


def join_by_dash(name):
    """
    if the name 'Room 1' is given, the output would be 'Room-1'
    """
    return "-".join(name.split())


BASE_CONVERSATION = '{ "conversation" : [] }'


# example string:
# '{"conv": [{"time": "1", "user": "me", "msg": "some message"},'
#           '{"time": "2", "user": "other", "msg": "some other message"}]}'


class Log(models.Model):
    """
    A log to save conversations
    """
    name = models.CharField(max_length=256, unique=True)
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
        return conversation

    def number_of_messages(self):
        return len(self.read()['conversation'])

    def parse_data(self):
        time_stamps = []
        messages = []
        users = []

        data = self.read()

        for msg in data['conversation']:
            time_stamps.append(msg['time'])
            messages.append(msg['msg'])
            if msg['user'] not in users:
                users.append(msg['user'])

        return time_stamps, messages, users
