# gameplay/forms.py  (or wherever you keep admin forms)
from django import forms
from gameplay.models import Game
from django.contrib.admin.helpers import ActionForm


class SeatUsersForm(ActionForm):
    """Extra field that will appear in the admin action bar."""
    game = forms.ModelChoiceField(
        queryset=Game.objects.filter(game_active=True),
        required=True,
        label="Game to seat users in",
    )