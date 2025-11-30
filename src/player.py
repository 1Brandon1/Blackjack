class Hand:
    """Represents a single hand of cards for a player (used for splits)."""
    def __init__(self, cards=None, bet=0):
        self.cards = cards if cards else []
        self.bet = bet
        self.insurance_bet = 0
        self.has_doubled = False
        self.finished = False  # True when the hand has completed its turn

    def add_card(self, card):
        self.cards.append(card)

    def value(self):
        """Calculate total hand value, adjusting for Aces as 1 or 11."""
        total = sum(c.value() for c in self.cards)
        aces = sum(1 for c in self.cards if c.rank == 'A')

        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    def is_blackjack(self):
        return len(self.cards) == 2 and self.value() == 21

    def can_split(self, balance):
        """Can split if exactly 2 cards of same rank and player has enough balance."""
        return (
            len(self.cards) == 2 and
            self.cards[0].rank == self.cards[1].rank and
            balance >= self.bet
        )

    def show(self):
        return " ".join(str(c) for c in self.cards)


class Player:
    def __init__(self, name="Player", start_balance=5000):
        self.name = name
        self.balance = start_balance
        self.hands = []  # Supports multiple hands after splitting

    def start_new_hand(self, bet):
        self.balance -= bet
        self.hands = [Hand(bet=bet)]

    def clear_hands(self):
        self.hands = []

    def all_hands_finished(self):
        return all(hand.finished for hand in self.hands)


class Dealer:
    def __init__(self):
        self.name = "Dealer"
        self.hand = Hand()

    def clear_hand(self):
        self.hand = Hand()

    def should_hit(self):
        return self.hand.value() < 17

    def show_hand(self, reveal_all=True):
        if not reveal_all and len(self.hand.cards) > 1:
            return f"[Hidden] {self.hand.cards[1]}"
        return " ".join(str(c) for c in self.hand.cards)
