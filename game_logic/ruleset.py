class Ruleset:
    @staticmethod
    def is_slap_valid(pile):
        if len(pile) < 2:
            return False

        # Check for double
        if pile[-1].rank == pile[-2].rank:
            return True

        # Check for sandwich
        if len(pile) >= 3 and pile[-1].rank == pile[-3].rank:
            return True

        # Check for marriage
        last_two = {pile[-1].rank, pile[-2].rank}
        if last_two == {'K', 'Q'}:
            return True

        if Ruleset.check_four_in_a_row(pile[-4:]):
            return True
        return False

    @staticmethod
    def is_face_card(card):
        return card.rank in ['J', 'Q', 'K', 'A']

    @staticmethod
    def get_face_card_plays(card):
        plays = {'J': 1, 'Q': 2, 'K': 3, 'A': 4}
        return plays.get(card.rank, 1)

    @staticmethod
    def check_four_in_a_row(cards):
        if len(cards) != 4:
            return False

        # Get two sets of values, one with Ace as 1, one with Ace as 14
        values_ace_low = [Ruleset.card_value(card, ace_high=False) for card in cards]
        values_ace_high = [Ruleset.card_value(card, ace_high=True) for card in cards]

        # Check ascending order (including wraparound)
        if Ruleset.is_ascending(values_ace_low) or Ruleset.is_ascending(values_ace_high):
            return True

        # Check descending order (including wraparound)
        if Ruleset.is_descending(values_ace_low) or Ruleset.is_descending(values_ace_high):
            return True

        return False

    @staticmethod
    def is_ascending(values):
        return values in ([1, 2, 3, 4], [11, 12, 13, 14], [13, 14, 1, 2])

    @staticmethod
    def is_descending(values):
        return values in ([4, 3, 2, 1], [14, 13, 12, 11], [2, 1, 14, 13])

    @staticmethod
    def card_value(card, ace_high=False):
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
                  '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}
        if ace_high:
            values['A'] = 14
        else:
            values['A'] = 1
        return values.get(card.rank, 0)