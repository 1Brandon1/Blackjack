from cards import Shoe
from player import Player, Dealer, Hand
import sys

class Game:
    def __init__(self, playerNames):
        self.shoe = Shoe()  # Initialise card shoe
        self.players = [Player(name) for name in playerNames]
        self.dealer = Dealer()

    def setupRound(self):
        self.dealer.clearHand()  # Reset dealer's hand
        self.players = [p for p in self.players if p.balance > 0]  # Remove broke players
        for player in self.players:
            player.clearHands()  # Reset each player's hands
        if not self.players:
            print("💸 All players are out of chips. Game over.")
            sys.exit()

    def takeBets(self):
        # Prompt each player to place a valid bet
        for player in self.players:
            while True:
                try:
                    raw = input(f"💰 {player.name}, you have {player.balance} chips. Place your bet: ")
                    amount = int(raw)
                    if amount <= 0:
                        raise ValueError("Bet must be positive.")
                    if amount > player.balance:
                        raise ValueError("Not enough balance to place bet.")
                    player.startNewHand(amount)
                    break
                except ValueError as e:
                    print(f"⚠️ {e}")
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Quitting game.")
                    sys.exit()

    def dealInitialCards(self):
        # Deal 2 cards to each hand and dealer
        for _ in range(2):
            for player in self.players:
                for hand in player.hands:
                    hand.addCard(self.shoe.drawCard())
            self.dealer.hand.addCard(self.shoe.drawCard())

    def offerInsurance(self):
        # Only offer if dealer's second card is an Ace
        if len(self.dealer.hand.cards) < 2 or self.dealer.hand.cards[1].rank != 'A':
            return

        print("\n⚠️ Dealer shows an Ace! Offering insurance...")
        for player in self.players:
            for hand in player.hands:
                if player.balance >= hand.bet // 2:
                    while True:
                        try:
                            choice = input(f"{player.name}, do you want insurance for hand ({hand.show()})? (y/n): ").strip().lower()
                            if choice in ['y', 'n']:
                                break
                            print("⚠️ Please enter 'y' or 'n'.")
                        except (EOFError, KeyboardInterrupt):
                            print("\n👋 Exiting game.")
                            sys.exit()
                    if choice == 'y':
                        insuranceAmount = hand.bet // 2
                        hand.insuranceBet = insuranceAmount  # Track insurance bet separately
                        player.balance -= insuranceAmount
                        print(f"{player.name} placed an insurance bet of {insuranceAmount} chips.")

    def playerTurns(self):
        for player in self.players:
            handIndex = 0
            while handIndex < len(player.hands):
                hand = player.hands[handIndex]

                if hand.finished:  # Skip finished hands
                    handIndex += 1
                    continue

                print(f"\n🎲 {player.name}'s Turn - Hand {handIndex + 1}: {hand.show()} [Value: {hand.value()}]")

                if hand.isBlackjack():
                    print("✅ Blackjack!")
                    hand.finished = True
                    handIndex += 1
                    continue

                if hand.value() >= 21:  # Auto-stand or bust
                    if hand.value() > 21:
                        print("❌ Busted!")
                    else:
                        print("🛑 You have 21. Automatically standing.")
                    hand.finished = True
                    handIndex += 1
                    continue

                # Build available actions
                actions = ['(h)it', '(s)tand']
                if len(hand.cards) == 2:  # Only first two cards allow these
                    if player.balance >= hand.bet:
                        actions.append('(d)ouble')
                    if hand.canSplit(player.balance):
                        actions.append('s(p)lit')
                    actions.append('s(u)rrender')

                actionPrompt = "➡️ Choose action " + ", ".join(actions) + ": "
                try:
                    action = input(actionPrompt).strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Exiting game.")
                    sys.exit()

                # Handle chosen action
                if action in ['hit', 'h']:
                    hand.addCard(self.shoe.drawCard())
                elif action in ['stand', 's']:
                    hand.finished = True
                    handIndex += 1
                elif action in ['double', 'd'] and len(hand.cards) == 2 and player.balance >= hand.bet:
                    player.balance -= hand.bet
                    hand.bet *= 2
                    hand.hasDoubled = True
                    hand.addCard(self.shoe.drawCard())
                    print(f"🃏 {hand.show()} [Value: {hand.value()}]")
                    hand.finished = True
                    handIndex += 1
                elif action in ['split', 'p'] and hand.canSplit(player.balance):
                    player.balance -= hand.bet
                    # Split into two hands
                    newHand1 = Hand(cards=[hand.cards[0]], bet=hand.bet)
                    newHand2 = Hand(cards=[hand.cards[1]], bet=hand.bet)
                    newHand1.addCard(self.shoe.drawCard())
                    newHand2.addCard(self.shoe.drawCard())
                    player.hands[handIndex] = newHand1
                    player.hands.insert(handIndex + 1, newHand2)
                    # Do not increment handIndex: process newHand1 next
                elif action in ['surrender', 'u'] and len(hand.cards) == 2:
                    refund = hand.bet // 2
                    player.balance += refund
                    print(f"💸 {player.name} surrenders. Half bet returned: {refund} chips.")
                    hand.bet = 0
                    hand.finished = True
                    handIndex += 1
                else:
                    print("⚠️ Invalid input.")

    def dealerTurn(self):
        print(f"\n🂠 Dealer's hand: {self.dealer.showHand()} [Value: {self.dealer.hand.value()}]")
        while self.dealer.shouldHit():  # Dealer hits until rules say stand
            self.dealer.hand.addCard(self.shoe.drawCard())
            print(f"🂡 Dealer hits: {self.dealer.showHand()} [Value: {self.dealer.hand.value()}]")

    def resolveRound(self):
        dealerScore = self.dealer.hand.value()
        dealerBlackjack = self.dealer.hand.isBlackjack()
        print(f"\n🔚 Dealer stands at {dealerScore}")

        for player in self.players:
            for handIndex, hand in enumerate(player.hands):
                bet = hand.bet
                playerScore = hand.value()
                print(f"\n💵 {player.name} - Hand {handIndex + 1}: {hand.show()} [Value: {playerScore}]")

                # Insurance resolution
                if hand.insuranceBet > 0:
                    if dealerBlackjack:
                        payout = hand.insuranceBet * 2
                        player.balance += payout
                        print(f"✅ {player.name} wins insurance bet! +{payout} chips.")
                    hand.insuranceBet = 0

                # Main bet resolution
                if hand.isBlackjack() and not dealerBlackjack:
                    winnings = int(bet * 2.5)
                    player.balance += winnings
                    print(f"🎉 Blackjack! +{winnings} chips.")
                elif dealerBlackjack:
                    print("❌ Dealer has Blackjack. You lose.")
                elif playerScore > 21:
                    print("💥 Busted.")
                elif dealerScore > 21 or playerScore > dealerScore:
                    winnings = bet * 2
                    player.balance += winnings
                    print(f"🏆 {player.name} wins! +{winnings} chips.")
                elif playerScore == dealerScore:
                    player.balance += bet
                    print("🤝 Push.")
                else:
                    print("❌ Dealer beats you.")

    def play(self):
        while True:
            self.setupRound()
            self.takeBets()
            self.dealInitialCards()
            print(f"\n🂠 Dealer shows: {self.dealer.hand.cards[1]}")
            self.offerInsurance()

            if self.dealer.hand.isBlackjack():
                print("\n💥 Dealer has Blackjack!")
                print(f"🂠 Dealer's hand: {self.dealer.showHand()} [Value: {self.dealer.hand.value()}]")
                self.resolveRound()
            else:
                self.playerTurns()
                if any(hand.value() <= 21 for player in self.players for hand in player.hands):
                    self.dealerTurn()
                self.resolveRound()

            # Ask to play again
            while True:
                try:
                    response = input("\n🔁 Play another round? (y/n): ").strip().lower()
                    if response in ['y', 'n']:
                        break
                    print("⚠️ Please enter 'y' or 'n'.")
                except (EOFError, KeyboardInterrupt):
                    response = 'n'
                    break
            if response == 'n':
                print("\n🃏 Thanks for playing! Goodbye.")
                break
