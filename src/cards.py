import random


class Card:
    def __init__(self, rank, suit):
        self.rank = rank  # Card rank, e.g., '2', 'J', 'A'
        self.suit = suit  # Card suit, e.g., 'Hearts', 'Spades'

    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  # Ace is counted as 11 by default
        return int(self.rank)

    def __str__(self):
        suit_symbols = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
        return f"{self.rank}{suit_symbols.get(self.suit)}"


class Shoe:
    def __init__(self, num_of_decks=6):
        self.num_of_decks = num_of_decks  # Number of decks in the shoe
        self.cards = []
        self.build_shoe()
        self.shuffle()

    def build_shoe(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks] * self.num_of_decks

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        if not self.cards:
            # Rebuild and reshuffle if empty
            self.build_shoe()
            self.shuffle()
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)
