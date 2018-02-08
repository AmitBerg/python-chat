from django.conf import settings
from django.utils.html import escape
from functools import wraps
import csv


from .exceptions import ClientError
from .models import Room


def catch_client_error(func):
    """
    Decorator to catch the ClientError exception and translate it into a reply.
    """

    @wraps(func)
    def inner(message):
        try:
            return func(message)
        except ClientError as e:
            # If we catch a client error, tell it to send an error string
            # back to the client on their reply channel
            e.send_to(message.reply_channel)

    return inner


def get_room_or_error(room_id, user):
    """
    Tries to fetch a room for the user, checking permissions along the way.
    """
    # Check if the user is logged in
    if not user.is_authenticated:
        raise ClientError("USER_HAS_TO_LOGIN")
    # Find the room they requested (by ID)
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        raise ClientError("ROOM_INVALID")
    # Check permissions
    if room.staff_only and not user.is_staff:
        raise ClientError("ROOM_ACCESS_DENIED")
    return room


def read(log_file):
    if log_file:
        if not log_file.endswith(".csv"):
            log_file += ".csv"
        conv = []
        with open(settings.LOGS_PATH + "/" + log_file, "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=' ', quotechar='|')
            for row in csv_reader:
                conv.append([escape(elm) for elm in row])
        return conv


def write(time, room_id, user, message):
    room = Room.objects.get(id=room_id)
    log_file = room.room_log.name
    with open(settings.LOGS_PATH + "/" + log_file + ".csv", 'a', newline="") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([time, room.title, user, message])
