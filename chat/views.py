from django.conf import settings
from django.http import Http404
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, reverse
from easy_rest.views import RestApiView, TemplateContextFetcherView
import os

from .models import Room, Log
from .utils import read


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


class ChatRoomsListView(LoginRequiredMixin, ListView):
    queryset = Room
    template_name = 'chat/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ChatRoomsListView, self).get_context_data()
        context['rooms'] = Room.objects.order_by('title')
        return context


class ChatRoomDetailView(DetailView):
    model = Room
    template_name = 'chat/single_room.html'


class StatisticsView(PermissionRequiredMixin, TemplateView):
    template_name = "chat/statistics.html"
    permission_required = 'user.is_superuser'


class FileView(PermissionRequiredMixin, TemplateContextFetcherView):
    template_name = "file.html"
    permission_required = 'user.is_superuser'

    # TODO loop over the conversation here, make here the Html and pass it by context
    def get_context_data(self, **kwargs):
        return {'random': read(self.request.path.split("/")[-1])}

    def get(self, request, *args, **kwargs):
        response = super(FileView, self).get(request, *args, **kwargs)
        file = self.request.path.split("/")[-1]
        if not file:
            raise Http404('"%s" does not exist' % file)
        path = os.path.join(settings.MEDIA_ROOT + "/chat/logs/", file)
        if not os.path.exists(path):
            raise Http404('"%s" does not exist' % path)
        return response


class FileListView(PermissionRequiredMixin, TemplateView):
    template_name = 'files.html'

    permission_required = 'user.is_superuser'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(FileListView, self).get_context_data()
        context['logs'] = Log.objects.order_by('name')
        return context
