from django.views.generic import DetailView, ListView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Room


@login_required
def index(request):
    """
    Root page view. This is essentially a single-page app, if you ignore the
    login and admin parts.
    """
    # Render that in the index template
    rooms = Room.objects.order_by("title")

    # Render that in the index template
    return render(request, "chat/index.html", {
        "rooms": rooms,
    })


class ChatRoomsListView(ListView):
    queryset = Room
    template_name = 'chat/rooms.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ChatRoomsListView, self).get_context_data()
        context['rooms'] = Room.objects.order_by('title')
        return context


class ChatRoomDetailView(DetailView):
    model = Room
    template_name = 'chat/single_room.html'
