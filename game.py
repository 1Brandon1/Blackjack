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
                if any(p.handValue() <= 21 for p in self.players):
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
                    player.placeBet(amount)
                    break
                except ValueError as e:
                    print(f"⚠️ Invalid bet: {e}")
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Quitting game.")
                    sys.exit()

    def dealInitialCards(self):
        for _ in range(2):
            for player in self.players:
                player.receiveCard(self.shoe.drawCard())
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
            if player.balance >= player.currentBet // 2:
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
                        insuranceAmount = player.currentBet // 2
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
            print(f"\n🎲 {player.name}'s Turn")
            while True:
                print(f"🃏 {player.showHand()} [Value: {player.handValue()}]")

                if player.isBlackjack():
                    print("✅ Blackjack!")
                    break

                if player.handValue() >= 21:
                    if player.handValue() > 21:
                        print("❌ Busted!")
                    elif player.handValue() == 21:
                        print("🛑 You have 21. Automatically standing.")
                    break

                # Build dynamic action prompt
                actions = ['(h)it', '(s)tand']
                if player.canDouble():
                    actions.append('(d)ouble')
                action_prompt = "➡️  Choose action " + ", ".join(actions) + ": "

                try:
                    action = input(action_prompt).strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Exiting game.")
                    sys.exit()

                if action in ['hit', 'h']:
                    player.receiveCard(self.shoe.drawCard())
                elif action in ['stand', 's']:
                    break
                elif action in ['double', 'd'] and player.canDouble():
                    player.doubleDown()
                    player.receiveCard(self.shoe.drawCard())
                    print(f"🃏 {player.showHand()} [Value: {player.handValue()}]")
                    break
                else:
                    print("⚠️ Invalid input.")

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
            playerScore = player.handValue()
            playerBlackjack = player.isBlackjack()
            bet = player.currentBet
            insurance = player.insuranceBet

            # Insurance resolution
            if insurance > 0:
                if dealerBlackjack:
                    payout = insurance * 2
                    player.balance += payout
                    print(f"✅ {player.name} wins insurance bet! +{payout} chips.")
                player.insuranceBet = 0

            # Main bet resolution
            if playerBlackjack and not dealerBlackjack:
                winnings = int(bet * 2.5)
                player.balance += winnings
                print(f"🎉 {player.name} has Blackjack! +{winnings} chips.")
            elif dealerBlackjack:
                print(f"❌ {player.name} loses. Dealer has Blackjack.")
            elif playerScore > 21:
                print(f"💥 {player.name} busted.")
            elif dealerScore > 21 or playerScore > dealerScore:
                winnings = bet * 2
                player.balance += winnings
                print(f"🏆 {player.name} wins! +{winnings} chips.")
            elif playerScore == dealerScore:
                player.balance += bet
                print(f"🤝 {player.name} pushes.")
            else:
                print(f"❌ Dealer beats {player.name}.")

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
