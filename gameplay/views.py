from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import register

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
    

class StartRoundAjaxView(View):
    def post(self, request, game_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        player, _ = Player.objects.get_or_create(user=request.user)
        if not game.players.filter(id=player.id).exists():
            game.players.add(player)
            player.sitting_in = True
            player.save()

        game.start_new_round()

        hands = {p.id: p.hand for p in game.players.all()}
        return JsonResponse({"hands": hands})
    


class JoinGameView(View):
    def post(self, request, game_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        player, _ = Player.objects.get_or_create(user=request.user)

        if not game.players.filter(id=player.id).exists():
            game.players.add(player)

        player.sitting_in = True
        player.is_folded = False
        player.is_all_in = False
        player.seat_position = game.players.count() - 1
        player.save()

        return redirect('gameplay:gameplay', game_id )