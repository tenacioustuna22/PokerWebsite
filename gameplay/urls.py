from django.urls import path
from .views import *


app_name = "gameplay"

urlpatterns = [
    path("<int:game_id>/", GameplayView.as_view(), name="gameplay"),
    path("lobby/", LobbyView.as_view(), name="lobby"),
    path("new/", CreateNewGame.as_view(), name="new_game"),
    path("<int:game_id>/start-ajax/", StartRoundAjaxView.as_view(), name="start_round_ajax"), 
    path("<int:game_id>/join/", JoinGameView.as_view(), name="join_game"),
]