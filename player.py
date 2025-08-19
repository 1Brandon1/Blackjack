class Player:
    def __init__(self, name="Player", startBalance=5000):
        self.name = name
        self.balance = startBalance
        self.hands = [[]]  # A list of hands to support splits
        self.bets = [0]
        self.insuranceBet = 0
        self.doubled = [False]

    def clearHand(self):
        self.hands = [[]]
        self.bets = [0]
        self.doubled = [False]
        self.insuranceBet = 0

    def receiveCard(self, handIndex, card):
        self.hands[handIndex].append(card)

    def showHand(self, handIndex):
        return ' '.join(str(card) for card in self.hands[handIndex])

    def handValue(self, handIndex):
        total = 0
        aces = 0
        for card in self.hands[handIndex]:
            val = card.value()
            total += val
            if card.rank == 'A':
                aces += 1
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def handValues(self):
        return [self.handValue(i) for i in range(len(self.hands))]

    def isBlackjack(self, handIndex):
        return len(self.hands[handIndex]) == 2 and self.handValue(handIndex) == 21

    def currentBet(self, handIndex):
        return self.bets[handIndex]

    def placeBet(self, handIndex, amount):
        if amount > self.balance:
            raise ValueError("Not enough chips to place bet.")
        self.bets[handIndex] = amount
        self.balance -= amount

    def placeInsurance(self, amount):
        if amount > self.balance:
            raise ValueError("Not enough chips for insurance.")
        self.insuranceBet = amount
        self.balance -= amount

    def canDouble(self, handIndex):
        return len(self.hands[handIndex]) == 2 and self.balance >= self.bets[handIndex]

    def doubleDown(self, handIndex):
        if not self.canDouble(handIndex):
            raise ValueError("Cannot double down.")
        self.balance -= self.bets[handIndex]
        self.bets[handIndex] *= 2
        self.doubled[handIndex] = True

    def canSplit(self, handIndex):
        hand = self.hands[handIndex]
        return (
            len(hand) == 2 and
            hand[0].rank == hand[1].rank and
            self.balance >= self.bets[handIndex]
        )

    def splitHand(self, handIndex, shoe):
        # Remove one card from the original hand
        original_card = self.hands[handIndex].pop()

        # Create a new hand with the split card
        newHand = [original_card]
        self.hands.append(newHand)

        # Draw one card to each hand
        self.hands[handIndex].append(shoe.drawCard())
        self.hands[-1].append(shoe.drawCard())

        # Add the new bet and doubled state
        self.balance -= self.bets[handIndex]
        self.bets.append(self.bets[handIndex])
        self.doubled.append(False)
    
class Dealer(Player):
    def __init__(self):
        super().__init__(name="Dealer")

    def shouldHit(self):
        return self.handValue() < 17