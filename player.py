from cards import Card

class Player:
    def __init__(self, name="Player", startBalance=5000):
        self.name = name
        self.hand = []
        self.balance = startBalance
        self.currentBet = 0
        self.insuranceBet = 0
        self.hasDoubled = False

    def clearHand(self):
        self.hand = []
        self.currentBet = 0
        self.insuranceBet = 0
        self.hasDoubled = False

    def receiveCard(self, card):
        self.hand.append(card)

    def showHand(self):
        return " ".join(str(c) for c in self.hand)
    
    def handValue(self):
        total = sum(card.value() for card in self.hand)
        aces = sum(1 for c in self.hand if c.rank == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def isBlackjack(self):
        return len(self.hand) == 2 and self.handValue() == 21
    
    def placeBet(self, amount):
        if amount > self.balance:
            raise ValueError("Not enough balance to place bet.")
        self.balance -= amount
        self.currentBet = amount

    def placeInsurance(self, amount):
        if amount > self.balance:
            raise ValueError("Not enough balance for insurance.")
        self.balance -= amount
        self.insuranceBet = amount

    def canDouble(self):
        return len(self.hand) == 2 and self.balance >= self.currentBet

    def doubleDown(self):
        if not self.canDouble():
            raise ValueError("Cannot double down right now.")
        self.balance -= self.currentBet
        self.currentBet *= 2
        self.hasDoubled = True

class Dealer(Player):
    def __init__(self):
        super().__init__(name="Dealer", startBalance=0)

    def shouldHit(self):
        return self.handValue() < 17

    def showHand(self, revealAll=True):
        if not revealAll and len(self.hand) > 1:
            return f"[Hidden] {self.hand[1]}"
        return " ".join(str(c) for c in self.hand)
