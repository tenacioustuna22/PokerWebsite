from django.urls import path
from .views import GameplayView, LobbyView



urlpatterns = [
    path("<int:game_id>/", GameplayView.as_view(), name="gameplay"),
    path("lobby/", LobbyView.as_view(), name="lobby")
]