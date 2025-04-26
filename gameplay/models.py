from django.db import models
from django.db.models import JSONField
from django.conf import settings
import random
from . import constants

class Deck(models.Model):

    game = models.OneToOneField(
        'Game',              
        on_delete=models.CASCADE,
        related_name='deck'
    )


    cards = JSONField(default=list, blank=True)
    community_cards = JSONField(default=list, blank=True)

    SUITS = ['S', 'C', 'H', 'D']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    def __str__(self):
        return f'Deck for {self.game}'
    
    def build_deck(self):
        deck = [(rank, suit) for rank in self.RANKS for suit in self.SUITS]
        random.shuffle(deck)
        self.cards = deck
        self.save()
    
    def draw(self, num_cards=1):
        drawn = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        self.save()
        return drawn
    
    def burn(self, num_cards=1):
        self.draw(num_cards)

    def deal_flop(self, num_cards=3):
        flop = self.draw(num_cards)
        self.community_cards += flop
        self.save()
    
    def deal_turn(self, num_cards=1):
        flop = self.draw(num_cards)
        self.community_cards += flop
        self.save()
    
    def deal_river(self, num_cards=1):
        flop = self.draw(num_cards)
        self.community_cards += flop
        self.save()

    def deal_to_player(self, player, num_cards=2):
        player.hand.clear()
        player.hand = self.draw(num_cards)
        player.save()
    
    def deal_to_all_players(self):
        for player in self.game.players.all():
            self.deal_to_player(player)
            player.save()



class Player(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='player_profile'
        )
    
    bet_amount = models.FloatField(default=0.0)
    last_bet = models.FloatField(default=0.0)
    beginning_money = models.FloatField(default=0.0)
    all_in_pot_amount = models.FloatField(default=0.0)
    all_in_difference = models.FloatField(default=0.0)

    hand = models.JSONField(default=list, blank=True)

    seat_position = models.PositiveIntegerField(default=0)
    
    sitting_in = models.BooleanField(default=False)
    is_folded = models.BooleanField(default=False)
    is_all_in = models.BooleanField(default=False)
    is_dealer = models.BooleanField(default=False)
    is_small_blind = models.BooleanField(default=False)
    is_big_blind = models.BooleanField(default=False)

    def update_money(self, amount: float):
        self.user.money += amount
        self.user.money = round(self.user.money, 2)
        self.save()

    def perform_check(self):
        pass

    def all_in(self):
        self.is_all_in = True
        self.is_folded = True
        self.save()
    
    def fold(self):
        self.is_folded = True
        self.save()

    def sit_in(self):
        self.sitting_in = True
        self.save()



class Game(models.Model):

    players = models.ManyToManyField(
        Player, 
        related_name='games', 
        blank=True
    )
    
    pot = models.FloatField(default=0.0)
    current_bet = models.FloatField(default=0.0)
    small_blind = models.FloatField(default=0.10)
    big_blind = models.FloatField(default=0.25)
     
    winner = models.ManyToManyField(Player, blank=True)
    winner_determined = models.BooleanField(default=False)
    game_active = models.BooleanField(default=True)

    dealer_seat_index = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Game #{self.id}"
    

    def players_list(self):
        return list(self.players.filter(sitting_in = True).order_by('seat_position'))
    

    def assign_seats(self):
        players = self.players_list
        if len(players) > 8:
            pass
        for i, player in enumerate(players):
            player.seat_position = i
            player.save()

        
    def rotate_dealer_and_blinds(self):
        players = self.players_list()
        num_players = len(players)
        if num_players < 2:
            return
        
        self.dealer_seat_index = (self.dealer_seat_index + 1) % num_players
        for p in players:
            if p.seat_position == self.dealer_seat_index:
                p.is_dealer = True
                p.is_small_blind = False
                p.is_big_blind = False
            if p.seat_position == (self.dealer_seat_index + 1):
                p.is_dealer = False
                p.is_small_blind = True
                p.is_big_blind = False
            if p.seat_position == (self.dealer_seat_index + 2):
                p.is_dealer = False
                p.is_small_blind = False
                p.is_big_blind = True
            p.save()
        self.save()

    
    def use_blinds(self):
        small_blind_player = next((p for p in self.players.all() if p.is_small_blind), None)
        if small_blind_player:
            self.bet(small_blind_player, self.small_blind)
        big_blind_player = next((p for p in self.players.all() if p.is_big_blind), None)
        if big_blind_player:
            self.bet(big_blind_player, self.big_blind)
    

    def bet(self, player: Player, amount: float) -> dict[str, str | bool]: # make sure to add success and fail views later on i think
        try:
            amount = float(amount)
        except ValueError:
            return {"success": False, "message": "Invalid Amount"}
        
        if player.is_folded:
            return {"success": True, "message": f"{player.user.username} has already folded."}
        
        if amount == player.last_bet and player.last_bet == self.current_bet:
            player.perform_check()
            return {"success": True, "message": f"{player.user.username} checks."}
        
        elif amount - player.last_bet == 0:
            player.fold()
            return {"success": True, "message": f"{player.user.username} folds."}
        
        elif amount - player.last_bet == player.money:
            player.update_money(-amount + player.last_bet)
            self.pot += (amount - player.last_bet)
            self.pot = round(self.pot, 2)
            player.last_bet = round(amount, 2)
            self.current_bet = max(self.current_bet, amount)
            self.current_bet = round(self.current_bet, 2)
            player.all_in()
            player.save()
            self.save()
            return {"success": True, "message": f"{player.user.username} is all in for {player.last_bet}!"}
        
        elif amount < 0:
            return {"success": False, "message": f"Amount cannot be negative {player.user.username}."}
        
        elif amount - player.last_bet > player.money:
            return {"success": False, "message": f"""{player.user.username}, you do not have enough money to bet 
                    {round(amount, 2)}, your available money is {player.money}"""}
        
        elif amount < self.current_bet and amount > 0:
            return {"success": False, "message": f"{player.user.username}, not enough to match the current bet. Type 0 to fold."}
        
        elif amount > self.current_bet and amount < 2 * self.current_bet:
            return {"success": False, "message": f"{player.user.username}, your raise must be at least double the current bet."}

        player.update_money(-amount + player.last_bet) 
        self.pot += (amount - player.last_bet)
        self.pot = round(self.pot, 2)
        player.last_bet = round(amount, 2)
        self.current_bet = max(self.current_bet, amount)
        player.save()
        return {"success": True, "message": f"{player.user.username} bets {player.last_bet}"}
    

    def betting_sequence(self, player: Player):
        old_current_bet = self.current_bet
        
        if player.last_bet == self.current_bet and self.current_bet != 0:
            return {"success": True, "message": "No action required"}
        
        total_bet = player.bet_amount + player.last_bet
        bet_result = self.bet(player, total_bet) # need to ask user for either their total bet, or how much more they would like to bet
        if bet_result["success"]:
            return bet_result
        if old_current_bet < self.current_bet:
            self.raise_protocol()


    def initial_betting_sequence(self, player: Player):
        players = self.players_list()
        big_blind_player = next((p for p in players if p.is_big_blind), None)
        if not big_blind_player:
            return {"success": False, "message": "No big blind assigned"}

        big_blind_index = None
        for i, p in enumerate(players):
            if p == big_blind_player:
                big_blind_index = i
                break
        
        start_index = (big_blind_index + 1) % len(players)
    
        for offset in range(len(players)):
            current_player = players[(start_index + offset) % len(players)]
            self.betting_sequence(current_player)
        
        if big_blind_player and (self.current_bet == big_blind_player.last_bet == self.big_blind):
            old_current_bet = self.current_bet
            total_bet = player.bet_amount + current_player.last_bet 
            bet_result = self.bet(current_player, total_bet) #need to ask user for either their total bet, or how much more they would like to bet
            if bet_result["success"]:
                return bet_result
            if old_current_bet < self.current_bet:
                self.raise_protocol()
    

    def post_betting_sequence(self):
        players = self.players_list()
        self.current_bet = 0
        for p in players:
            if not p.is_folded:
                p.last_bet = 0
                self.betting_sequence(p)

  
  
    def raise_protocol(self):
        players = self.players_list()
        num_players = len(players)

        
        last_raiser_index = None
        for i, p in enumerate(players):
            if p.last_bet == self.current_bet and p.last_bet != 0:
                last_raiser_index = i

        if last_raiser_index is None:
            return  
        
        start_index = (last_raiser_index + 1) % num_players

        for i in range(start_index, start_index + num_players - 1):  
            p = players[i % num_players]  

            if p.last_bet < self.current_bet: 
                if p.is_folded:
                    continue
                self.betting_sequence(p)


    def calculate_all_in_amounts(self):
        players = self.players_list()
        for p in players:
            if p.is_all_in:
                p.all_in_pot_amount = self.pot
                for playa in players:
                    if playa.last_bet < p.last_bet:
                        if playa is p:
                            continue
                        playa.all_in_difference += p.last_bet - playa.last_bet 
                playa.all_in_pot_amount -= playa.all_in_difference



    def sort_players_all_in(self):
        players = self.players_list()
        for p in players:
            if p.is_all_in:
                p.is_folded = False
        all_in_players = [player for player in players if player.is_all_in]
        all_in_players.sort(key=lambda player: player.beginning_money)
        for player in all_in_players: 
            self.determine_winner(self.deck)
            if self.winner[0] == player and len(self.winner) == 1:
                winning_amount = player.all_in_pot_amount
                
                player.update_money(player.all_in_pot_amount)
                
                for p in self.players:
                    p.all_in_pot_amount -= winning_amount
                self.pot -= winning_amount
                
                for i, current_player in enumerate(all_in_players):
                    if i < len(all_in_players) - 1:
                        next_player = all_in_players[i+1]
                        next_player.all_in_pot_amount -= player.all_in_pot_amount
                    elif self.pot == current_player.all_in_pot_amount:
                        break
                    else:
                        self.pot -= player.all_in_pot_amount
            elif len(self.winner) != 1 and player in self.winner:
                num_winners = len(self.winner)
                share = player.all_in_pot_amount / num_winners
                player.update_money(share)
                self.pot -= share
                for p in players:
                    p.all_in_pot_amount -= share
            player.fold()



    def check_for_all_ins(self):
        players = self.players_list()
        if len([player for player in players if not player.is_all_in]) == 1:
            return True
        else:
            return False
        


    def if_everyone_folds(self):
        players = self.players_list()
        active_players = [player for player in players if not player.is_folded or player.is_all_in]
        if len(active_players) == 1:
            winner = active_players[0]
            self.winner = [winner]
            self.winner_determined = True
            self.award_money_to_winner()
            return True
        return False
    


    def determine_winner(self, deck: Deck):
        players = self.players_list()
        if all(p.is_folded for p in players):
            pass
        else:
            """
            After all betting is done and community cards are dealt,
            figure out who wins among non-folded players using tie-break logic.
            """
            # rank_names for printing
            rank_names = {
                1: "Straight Flush",
                2: "Four of a Kind",
                3: "Full House",
                4: "Flush",
                5: "Straight",
                6: "Three of a Kind",
                7: "Two Pair",
                8: "One Pair",
                9: "High Card"
            }


            community = deck.community_cards  # 5 community cards in deck.community

            # Evaluate each player's best 7-card hand
            results = []
            active_players = [p for p in players if not p.is_folded]
            for p in active_players:
                seven_cards = p.hand + community  # 7 total (2 hole, 5 community)
                cat, tie = constants.evaluate_7card_hand_detailed(seven_cards)
                results.append((p, (cat, tie)))

            # Now pick the single best or tie
            # best_hand = min(results, key=??) but we must do custom compare:
            # We'll do a simple pass:
            best_cat, best_tie = results[0][1]
            winners = [results[0][0]]  # the player objects

            for (p, (cat, tie)) in results[1:]:
                if cat < best_cat:
                    best_cat, best_tie = cat, tie
                    winners = [p]
                elif cat == best_cat:
                    if tie > best_tie:
                        best_cat, best_tie = cat, tie
                        winners = [p]
                    elif tie == best_tie:
                        winners.append(p)
            self.winner_determined = True
            self.save()


  
    def award_money_to_winner(self):
        if len(self.winner) == 1:
            sole_winner = self.winner[0]
            sole_winner.update_money(self.pot)
            return True
        else:
            num_winners = len(self.winner)
            share = self.pot / num_winners
            for w in self.winner:
                w.update_money(share)
            return False


    
    def start_new_round(self):
        players = self.players_list()
        for p in players:
            p.is_folded = False
            p.is_all_in = False
            p.last_bet = 0
            p.beginning_money = p.user.money
            p.all_in_pot_amount = 0
            p.all_in_difference = 0
            p.save()
        
        self.deck.build_deck()
        self.deck.deal_to_all_players()
        self.dealer_seat_index = (self.dealer_seat_index + 1) % len(players)
        self.current_bet = 0
        self.pot = 0
        self.winner.clear()
        self.winner_determined = False
        self.use_blinds()
        self.save()



    def play_one_round(self):
        players = self.players_list()
        while True:
            skip_betting = False
            self.start_new_round()

            self.initial_betting_sequence()
            self.calculate_all_in_amounts()
            if self.check_for_all_ins():
                skip_betting = True
            if self.if_everyone_folds():
                return

            self.deck.deal_flop()
            if not skip_betting:
                self.post_betting_sequence()
                self.calculate_all_in_amounts()
                if self.check_for_all_ins():
                    skip_betting = True
            if self.if_everyone_folds():
                return

            self.deck.deal_turn()
            if not skip_betting:
                self.post_betting_sequence()
                self.calculate_all_in_amounts()
                if self.check_for_all_ins():
                    skip_betting = True
            if self.if_everyone_folds():
                return

            self.deck.deal_river()
            if not skip_betting:
                self.post_betting_sequence()
                self.calculate_all_in_amounts()
            if self.if_everyone_folds():
                return

            self.sort_players_all_in()

            self.determine_winner()

            self.award_money_to_winner()
            if len(players) < 2:
                break