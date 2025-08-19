import random

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  
        return int(self.rank)

    def __str__(self):
        suitSymbols = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
        return f"{self.rank}{suitSymbols.get(self.suit)}"

class Shoe:
    def __init__(self, numOfDecks=6):
        self.numOfDecks = numOfDecks
        self.cards = []
        self.buildShoe()
        self.shuffle()

    def buildShoe(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks] * self.numOfDecks

    def shuffle(self):
        random.shuffle(self.cards)

    def drawCard(self):
        if not self.cards:
            self.buildShoe()
            self.shuffle()
        return self.cards.pop()
    
    def __len__(self):
        return len(self.cards)
