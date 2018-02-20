from django.utils.safestring import mark_safe
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from easy_rest.views import TemplateContextFetcherView, RestApiView

import random

from .models import Room, PrivateRoom, Log, join_by_dash
from .statistics import msg_count_by_user, word_count


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(reverse("homepage"))
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


class ChatRoomsListView(LoginRequiredMixin, generic.ListView):
    queryset = Room
    template_name = 'chat/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ChatRoomsListView, self).get_context_data()
        context['rooms'] = Room.objects.exclude_private()
        context['private_rooms'] = PrivateRoom.objects.my_private_rooms(user=self.request.user)
        return context


class ChatRoomDetailView(generic.DetailView):
    model = Room
    template_name = 'chat/single_room.html'


class StatisticsView(PermissionRequiredMixin, generic.TemplateView):
    template_name = "chat/statistics.html"
    permission_required = 'user.is_superuser'

    def get_context_data(self, **kwargs):
        context = super(StatisticsView, self).get_context_data(**kwargs)
        context["rooms"] = Room.objects.get_rooms_with_data()
        return context


class StatisticsApiView(PermissionRequiredMixin, RestApiView):
    permission_required = 'user.is_superuser'
    function_field_name = 'action'
    api_allowed_methods = ['get_log_data']

    def get_log_data(self, data):
        rooms = Room.objects.filter(pk__in=eval(data["room_pks"]))
        log_names = [join_by_dash(room.title) for room in rooms]
        logs = Log.objects.filter(name__in=log_names)
        return {"words": word_count(logs), "count": msg_count_by_user(logs)}


class ConversationView(PermissionRequiredMixin, TemplateContextFetcherView):
    template_name = "conversation.html"
    permission_required = 'user.is_superuser'

    def get_context_data(self, **kwargs):
        pk = self.request.path.split("/")[-1]
        log = Log.objects.get(pk=pk)
        conversation = log.prettify_conversation()
        num = log.number_of_messages()
        return {'conversation': conversation, 'num': num}


class ConversationListView(PermissionRequiredMixin, generic.TemplateView):
    template_name = 'conversations.html'
    permission_required = 'user.is_superuser'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ConversationListView, self).get_context_data()
        logs = Log.objects.order_by('name')
        # prettify the names
        for log in logs:
            log.name = log.name.replace("-", " ")
        context['logs'] = logs
        return context


class PrivateRoomView(UserPassesTestMixin, generic.DetailView):
    model = PrivateRoom
    template_name = 'chat/private_room.html'

    def test_func(self):
        cur_room = (PrivateRoom.objects.get(pk=self.get_object().pk))
        user_rooms = PrivateRoom.objects.my_private_rooms(self.request.user)
        return cur_room in user_rooms

    def get_permission_denied_message(self):
        choices = ["You are not allowed in the room ", "Nah uh! you are not getting into", "HELL NO! get away from"]
        return mark_safe(
            random.choice(choices) + " <span style='font-weight: bold;'>{}<span>".format(self.get_object()))

    def handle_no_permission(self):
        message = self.get_permission_denied_message()
        messages.error(request=self.request, message=message)
        return redirect(reverse("homepage"))

    def get_context_data(self, **kwargs):
        ctx = super(PrivateRoomView, self).get_context_data(**kwargs)
        # the user is the owner
        if self.request.user.id == self.get_object().owner_id:
            ctx['owner_button'] = " "
        return ctx


class CreatePrivateRoom(generic.CreateView):
    model = PrivateRoom
    fields = ['title', 'users']
    template_name = 'chat/private_room_create.html'
    success_url = "/"


class UpdatePrivateRoom(UserPassesTestMixin, generic.UpdateView):
    model = PrivateRoom
    fields = ['users']
    template_name = 'chat/private_room_update.html'

    def test_func(self):
        return self.request.user.id == self.get_object().owner_id

    def get_success_url(self):
        return reverse("chat:single_private_room", kwargs={"pk": self.get_object().pk})
