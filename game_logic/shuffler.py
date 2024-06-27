import random


class Shuffler:
    @staticmethod
    def shuffle(deck):
        # Fisher-Yates Shuffle
        for i in range(len(deck) - 1, 0, -1):
            j = random.randint(0, i)
            deck[i], deck[j] = deck[j], deck[i]
        return deck
