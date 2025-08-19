from cards import Shoe
from player import Player, Dealer
import sys

class Game:
    def __init__(self, playerNames):
        self.shoe = Shoe()
        self.players = [Player(name) for name in playerNames]
        self.dealer = Dealer()

    def play(self):
        while True:
            self.setupRound()
            self.takeBets()
            self.dealInitialCards()
            self.showDealerUpcard()
            self.offerInsurance()

            if self.dealer.isBlackjack():
                self.handleDealerBlackjack()
            else:
                self.playerTurns()
                if any(handValue <= 21 for player in self.players for handValue in player.handValues()):
                    self.dealerTurn()
                self.resolveRound()

            if not self.askToPlayAgain():
                print("\n🃏 Thanks for playing! Goodbye.")
                break

    def setupRound(self):
        self.dealer.clearHand()
        self.players = [p for p in self.players if p.balance > 0]
        for player in self.players:
            player.clearHand()

        if not self.players:
            print("💸 All players are out of chips. Game over.")
            sys.exit()

    def takeBets(self):
        for player in self.players:
            while True:
                try:
                    raw = input(f"💰 {player.name}, you have {player.balance} chips. Place your bet: ")
                    amount = int(raw)
                    if amount <= 0:
                        raise ValueError("⚠️ Bet must be positive.")
                    player.placeBet(0, amount)
                    break
                except ValueError as e:
                    print(f"⚠️ Invalid bet: {e}")
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Quitting game.")
                    sys.exit()

    def dealInitialCards(self):
        for _ in range(2):
            for player in self.players:
                player.receiveCard(0, self.shoe.drawCard())
            self.dealer.receiveCard(self.shoe.drawCard())

    def showDealerUpcard(self):
        if len(self.dealer.hand) >= 2:
            print(f"\n🂠 Dealer shows: {self.dealer.hand[1]}")
        else:
            print("⚠️ Dealer doesn't have enough cards to show.")

    def offerInsurance(self):
        if len(self.dealer.hand) < 2 or self.dealer.hand[1].rank != 'A':
            return

        print("\n⚠️ Dealer shows an Ace! Offering insurance...")
        for player in self.players:
            if player.balance >= player.currentBet(0) // 2:
                while True:
                    try:
                        choice = input(f"{player.name}, do you want insurance? (y/n): ").strip().lower()
                        if choice in ['y', 'n']:
                            break
                        print("⚠️ Please enter 'y' or 'n'.")
                    except (EOFError, KeyboardInterrupt):
                        print("\n👋 Exiting game.")
                        sys.exit()

                if choice == 'y':
                    try:
                        insuranceAmount = player.currentBet(0) // 2
                        player.placeInsurance(insuranceAmount)
                        print(f"{player.name} placed an insurance bet of {insuranceAmount} chips.")
                    except ValueError as e:
                        print(f"❌ Insurance failed: {e}")

    def handleDealerBlackjack(self):
        print("\n💥 Dealer has Blackjack!")
        print(f"🂠 Dealer's hand: {self.dealer.showHand()} [Value: {self.dealer.handValue()}]")
        self.resolveRound()

    def playerTurns(self):
        for player in self.players:
            handIndex = 0
            while handIndex < len(player.hands):
                print(f"\n🎲 {player.name}'s Turn — Hand {handIndex + 1}")
                while True:
                    value = player.handValue(handIndex)
                    print(f"🃏 {player.showHand(handIndex)} [Value: {value}]")

                    if player.isBlackjack(handIndex):
                        print("✅ Blackjack!")
                        break
                    if value >= 21:
                        if value > 21:
                            print("❌ Busted!")
                        break

                    options = "(h)it, (s)tand"
                    if player.canDouble(handIndex):
                        options += ", (d)ouble"
                    if player.canSplit(handIndex):
                        options += ", s(p)lit"

                    try:
                        action = input(f"➡️  Choose action {options}: ").strip().lower()
                    except (EOFError, KeyboardInterrupt):
                        print("\n👋 Exiting game.")
                        sys.exit()

                    if action in ['hit', 'h']:
                        player.receiveCard(handIndex, self.shoe.drawCard())
                    elif action in ['stand', 's']:
                        break
                    elif action in ['d', 'double'] and player.canDouble(handIndex):
                        player.doubleDown(handIndex)
                        player.receiveCard(handIndex, self.shoe.drawCard())
                        print(f"🃏 {player.showHand(handIndex)} [Value: {player.handValue(handIndex)}]")
                        break
                    elif action in ['p', 'split'] and player.canSplit(handIndex):
                        player.splitHand(handIndex, self.shoe)
                        print("🪓 Hand split!")
                        break  # Restart with this hand from 0
                    else:
                        print("⚠️ Invalid input.")
                handIndex += 1

    def dealerTurn(self):
        print(f"\n🂠 Dealer's hand: {self.dealer.showHand()} [Value: {self.dealer.handValue()}]")
        while self.dealer.shouldHit():
            self.dealer.receiveCard(self.shoe.drawCard())
            print(f"🂡 Dealer hits: {self.dealer.showHand()} [Value: {self.dealer.handValue()}]")

    def resolveRound(self):
        dealerScore = self.dealer.handValue()
        dealerBlackjack = self.dealer.isBlackjack()
        print(f"\n🔚 Dealer stands at {dealerScore}")

        for player in self.players:
            for i in range(len(player.hands)):
                score = player.handValue(i)
                blackjack = player.isBlackjack(i)
                bet = player.currentBet(i)
                insurance = player.insuranceBet

                if insurance > 0:
                    if dealerBlackjack:
                        payout = insurance * 2
                        player.balance += payout
                        print(f"✅ {player.name} wins insurance bet! +{payout} chips.")
                    player.insuranceBet = 0

                label = f"{player.name} (Hand {i + 1})" if len(player.hands) > 1 else player.name

                if blackjack and not dealerBlackjack:
                    winnings = int(bet * 2.5)
                    player.balance += winnings
                    print(f"🎉 {label} has Blackjack! +{winnings} chips.")
                elif dealerBlackjack:
                    print(f"❌ {label} loses. Dealer has Blackjack.")
                elif score > 21:
                    print(f"💥 {label} busted.")
                elif dealerScore > 21 or score > dealerScore:
                    winnings = bet * 2
                    player.balance += winnings
                    print(f"🏆 {label} wins! +{winnings} chips.")
                elif score == dealerScore:
                    player.balance += bet
                    print(f"🤝 {label} pushes.")
                else:
                    print(f"❌ Dealer beats {label}.")

    def askToPlayAgain(self):
        while True:
            try:
                response = input("\n🔁 Play another round? (y/n): ").strip().lower()
                if response in ['y', 'n']:
                    return response == 'y'
                print("⚠️ Please enter 'y' or 'n'.")
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Exiting game.")
                return False