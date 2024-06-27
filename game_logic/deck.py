from .card import Card
from .shuffler import Shuffler


class Deck:
    __slots__ = "cards"

    def __init__(self):
        self.cards = [Card(suit, rank) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']
                      for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']]

    def shuffle(self):
        self.cards = Shuffler.shuffle(self.cards)
