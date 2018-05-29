import json
import pytz
from datetime import datetime

from channels import Channel
from channels.auth import channel_session_user_from_http, channel_session_user

from django.utils.html import escape
from django.contrib.auth.models import User

from bot.bot import broback
from .settings import NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS, MSG_TYPE_ENTER, MSG_TYPE_LEAVE
from .utils import catch_client_error, get_room_or_error
from .models import Room
from .exceptions import ClientError

TIME_ZONE = pytz.timezone("Israel")


# This decorator copies the user from the HTTP session (only available in
# websocket.connect or http.request messages) to the channel session (available
# in all consumers with the same reply_channel, so all three here)
@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({"accept": True})
    message.channel_session['rooms'] = []


@channel_session_user
def ws_disconnect(message):
    # Unsubscribe from any connected rooms
    for room_id in message.channel_session.get("rooms", set()):
        try:
            room = Room.objects.get(pk=room_id)
            # Removes us from the room's send group. If this doesn't get run,
            # we'll get removed once our first reply message expires.
            room.websocket_group.discard(message.reply_channel)
        except Room.DoesNotExist:
            pass


# Unpacks the JSON in the received WebSocket frame and puts it onto a channel
# of its own with a few attributes extra so we can route it
# This doesn't need @channel_session_user as the next consumer will have that,
# and we preserve message.reply_channel (which that's based on)
def ws_receive(message):
    """All WebSocket frames have either a text or binary payload; we decode the
    text part here assuming it's JSON.
    You could easily build up a basic framework that did this encoding/decoding
    for you as well as handling common errors."""
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    Channel("chat.receive").send(payload)


# Channel_session_user loads the user out from the channel session and presents
# it as message.user. There's also a http_session_user if you want to do this on
# a low-level HTTP handler, or just channel_session if all you want is the
# message.channel_session object without the auth fetching overhead.
@catch_client_error
@channel_session_user
def chat_join(message):
    # Find the room they requested (by ID) and add ourselves to the send group
    # Note that, because of channel_session_user, we have a message.user
    # object that works just like request.user would. Security!
    room = get_room_or_error(message["room"], message.user)

    room.users.add(message.user)

    # Send a "enter message" to the room if available
    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        room.send_message("Has joined the room", message.user, MSG_TYPE_ENTER)

    # OK, add them in. The websocket_group is what we'll send messages
    # to so that everyone in the chat room gets them.
    room.websocket_group.add(message.reply_channel)
    message.channel_session['rooms'] = list(set(message.channel_session['rooms']).union([room.id]))
    # Send a message back that will prompt them to open the room
    # Done server-side so that we could, for example, make people
    # join rooms automatically.
    message.reply_channel.send({
        "text": json.dumps({
            "join": str(room.id),
            "title": room.title,
        }),
    })


@channel_session_user
@catch_client_error
def chat_leave(message):
    room = get_room_or_error(message["room"], message.user)

    room.users.remove(message.user)

    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        room.send_message("Has left the room", message.user, MSG_TYPE_LEAVE)

    room.websocket_group.discard(message.reply_channel)
    message.channel_session['rooms'] = list(set(message.channel_session['rooms']).difference([room.id]))
    message.reply_channel.send({
        "text": json.dumps({
            "leave": str(room.id),
        }),
    })


@channel_session_user
@catch_client_error
def chat_send(message):
    if int(message['room']) not in message.channel_session['rooms']:
        raise ClientError("ROOM_ACCESS_DENIED")
    # get the room
    room = get_room_or_error(message["room"], message.user)
    # log the message
    room.room_log.add_message(
        {"time": datetime.now(TIME_ZONE).strftime('%Y-%m-%d %H:%M:%S'), "user": message.user.username,
         "msg": escape(message['message'])})
    room.send_message(message["message"], message.user)
    # send bot reply
    if room.has_bot:
        if room.users.count() <= 2:
            response = broback(message['message'])
        else:
            response = broback(message['message'], True)

        if response:

            bot = User.objects.get_or_create(first_name="Bro", last_name="Bot", username="Brobot", password="brobot",
                                             email="bro@bot.com")
            # get_or create returns a tuple, the first val is the user
            # second is a boolean saying if its a "get" or "create"
            room.room_log.add_message(
                {"time": datetime.now(TIME_ZONE).strftime('%Y-%m-%d %H:%M:%S'), "user": bot[0].username,
                 "msg": response})
            room.send_message(response, bot[0])
