from django.urls import path
from .views import GameplayView, LobbyView, CreateNewGame

app_name = "gameplay"

urlpatterns = [
    path("<int:game_id>/", GameplayView.as_view(), name="gameplay"),
    path("lobby/", LobbyView.as_view(), name="lobby"),
    path("new/", CreateNewGame.as_view(), name="new_game")
]