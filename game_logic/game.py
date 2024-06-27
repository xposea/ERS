from .deck import Deck
from .player import Player
from .ruleset import Ruleset


class ERSGame:
    def __init__(self, players):
        self.deck = Deck()
        self.players = [Player(name) for name in players]
        self.all_players = self.players.copy()
        self.pile = []
        self.current_player_index = 0
        self.ruleset = Ruleset()
        self.face_card_player = None
        self.remaining_plays = 0

    def start_game(self):
        self.deck.shuffle()
        self.deal_cards()

    def deal_cards(self):
        while len(self.deck.cards) > 0:
            for player in self.players:
                if len(self.deck.cards) > 0:
                    player.add_card(self.deck.cards.pop())

    def play_turn(self):
        if self.remaining_plays > 0:
            player = self.face_card_player
            self.remaining_plays -= 1
        else:
            player = self.current_player
            self.face_card_player = None

        if player.has_cards():
            card = player.play_card()
            self.pile.append(card)

            if self.ruleset.is_face_card(card):
                self.handle_face_card(player, card)
            elif self.remaining_plays == 0:
                self.next_player()
        else:
            self.remove_player(player)

        if self.remaining_plays == 0 and self.face_card_player:
            self.face_card_player.add_cards(self.pile)
            self.pile = []
            self.current_player_index = self.players.index(self.face_card_player)
            self.face_card_player = None

    def attempt_slap(self, player):
        if self.ruleset.is_slap_valid(self.pile):
            player.add_cards(self.pile)
            self.pile = []
            if player not in self.players:
                self.players.append(player)  # Slap back in
            self.current_player_index = self.players.index(player)
            self.face_card_player = None
            self.remaining_plays = 0
            return True
        else:
            if player.has_cards():
                player.burn_card(self.pile)
            return False

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
        if len(self.players) == 1:
            print(f"Game over! {self.players[0].name} wins!")

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def is_game_over(self):
        return len(self.players) == 1

    def get_winner(self):
        if self.is_game_over():
            return self.players[0]
        return None

    def can_players_slap(self):
        return len(self.pile) >= 2
