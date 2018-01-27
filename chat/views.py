from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, reverse

from .models import Room


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
