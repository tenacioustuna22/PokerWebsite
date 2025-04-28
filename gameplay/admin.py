
"""
from django.contrib import admin
from .models import Game, Player, Deck

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'pot', 'current_bet', 'game_active', 'winner_determined')  # show these fields in list view
    search_fields = ('id',)  # allow search by game id
    list_filter = ('game_active', 'winner_determined')  # add sidebar filters
    filter_horizontal = ('players', 'winner')  # makes multi-select boxes nicer in edit form

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'seat_position', 'sitting_in', 'is_folded', 'is_all_in')
    search_fields = ('user__username',)
    list_filter = ('sitting_in', 'is_folded', 'is_all_in')

@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('id', 'game')
"""




from django.contrib import admin
from django.contrib.auth import get_user_model
from gameplay.models import Game, Player
from gameplay.forms import SeatUsersForm

User = get_user_model()

def seat_users(modeladmin, request, queryset):
    """Admin action: seat selected users in the chosen game."""
    game_id = request.POST.get('game')
    game = Game.objects.get(pk=game_id)

    added = 0
    for user in queryset:
        player, _ = Player.objects.get_or_create(user=user)
        if not game.players.filter(id=player.id).exists():
            player.sitting_in = True
            player.seat_position = game.players.count()
            player.save()
            game.players.add(player)
            added += 1

    modeladmin.message_user(request, f"{added} users seated in Game #{game.id}")

seat_users.short_description = "Seat selected users in chosen game"

class UserAdmin(admin.ModelAdmin):
    actions = [seat_users]          # the action itself
    action_form = SeatUsersForm     # adds the <select name="game"> box
    list_display = ("username", "is_staff", "is_superuser")

# replace the stock User admin with our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)