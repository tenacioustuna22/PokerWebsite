from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, View


from .models import *

class GameplayView(DetailView):
    model = Game
    template_name = "gameplay/gameplay.html"
    context_object_name = "game"
    pk_url_kwarg = "game_id"  

class LobbyView(ListView):
    model = Game
    template_name = "gameplay/lobby.html"
    context_object_name = "game"

    def get_queryset(self):
        return Game.objects.filter(game_active=True).order_by("-id")

class CreateNewGame(View):
    def post(self, request, *args, **kwargs):
        game = Game.objects.create()    
        return redirect("gameplay:gameplay", game_id=game.id)