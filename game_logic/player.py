class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.is_active = True

    def add_card(self, card):
        self.hand.append(card)
        self.is_active = True

    def add_cards(self, cards):
        self.hand.extend(cards)
        self.is_active = True

    def play_card(self):
        if self.has_cards():
            return self.hand.pop(0)
        else:
            self.is_active = False
            raise ValueError(f"{self.name} has no cards to play.")

    def has_cards(self):
        return len(self.hand) > 0

    def card_count(self):
        return len(self.hand)

    def burn_card(self, pile):
        if self.has_cards():
            card = self.hand.pop(0)
            pile.insert(0, card)
        else:
            print(f"{self.name} has no cards to burn.")
            self.is_active = False

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        return f"Player {self.name}: {len(self.hand)} cards ({status})"
