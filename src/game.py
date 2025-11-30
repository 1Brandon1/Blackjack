from cards import Shoe
from player import Player, Dealer, Hand
import sys


class Game:
    def __init__(self, player_names):
        self.shoe = Shoe()  # Initialise card shoe
        self.players = [Player(name) for name in player_names]
        self.dealer = Dealer()

    def setup_round(self):
        self.dealer.clear_hand()  # Reset dealer's hand
        self.players = [p for p in self.players if p.balance > 0]  # Remove broke players
        for player in self.players:
            player.clear_hands()  # Reset each player's hands
        if not self.players:
            print("💸 All players are out of chips. Game over.")
            sys.exit()

    def take_bets(self):
        """Prompt each player to place a valid bet."""
        for player in self.players:
            while True:
                try:
                    raw = input(f"💰 {player.name}, you have {player.balance} chips. Place your bet: ")
                    amount = int(raw)
                    if amount <= 0:
                        raise ValueError("Bet must be positive.")
                    if amount > player.balance:
                        raise ValueError("Not enough balance to place bet.")
                    player.start_new_hand(amount)
                    break
                except ValueError as e:
                    print(f"⚠️ {e}")
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Quitting game.")
                    sys.exit()

    def deal_initial_cards(self):
        """Deal 2 cards to each hand and dealer."""
        for _ in range(2):
            for player in self.players:
                for hand in player.hands:
                    hand.add_card(self.shoe.draw_card())
            self.dealer.hand.add_card(self.shoe.draw_card())

    def offer_insurance(self):
        """Only offer if dealer's second card is an Ace."""
        if len(self.dealer.hand.cards) < 2 or self.dealer.hand.cards[1].rank != 'A':
            return

        print("\n⚠️ Dealer shows an Ace! Offering insurance...")
        for player in self.players:
            for hand in player.hands:
                if player.balance >= hand.bet // 2:
                    while True:
                        try:
                            choice = input(
                                f"{player.name}, do you want insurance for hand ({hand.show()})? (y/n): "
                            ).strip().lower()
                            if choice in ['y', 'n']:
                                break
                            print("⚠️ Please enter 'y' or 'n'.")
                        except (EOFError, KeyboardInterrupt):
                            print("\n👋 Exiting game.")
                            sys.exit()
                    if choice == 'y':
                        insurance_amount = hand.bet // 2
                        hand.insurance_bet = insurance_amount
                        player.balance -= insurance_amount
                        print(f"{player.name} placed an insurance bet of {insurance_amount} chips.")

    def player_turns(self):
        for player in self.players:
            hand_index = 0
            while hand_index < len(player.hands):
                hand = player.hands[hand_index]

                if hand.finished:  # Skip finished hands
                    hand_index += 1
                    continue

                print(f"\n🎲 {player.name}'s Turn - Hand {hand_index + 1}: {hand.show()} [Value: {hand.value()}]")

                if hand.is_blackjack():
                    print("✅ Blackjack!")
                    hand.finished = True
                    hand_index += 1
                    continue

                if hand.value() >= 21:  # Auto-stand or bust
                    if hand.value() > 21:
                        print("❌ Busted!")
                    else:
                        print("🛑 You have 21. Automatically standing.")
                    hand.finished = True
                    hand_index += 1
                    continue

                # Build available actions
                actions = ['(h)it', '(s)tand']
                if len(hand.cards) == 2:  # Only first two cards allow these
                    if player.balance >= hand.bet:
                        actions.append('(d)ouble')
                    if hand.can_split(player.balance):
                        actions.append('s(p)lit')
                    actions.append('s(u)rrender')

                action_prompt = "➡️ Choose action " + ", ".join(actions) + ": "
                try:
                    action = input(action_prompt).strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Exiting game.")
                    sys.exit()

                # Handle chosen action
                if action in ['hit', 'h']:
                    hand.add_card(self.shoe.draw_card())
                elif action in ['stand', 's']:
                    hand.finished = True
                    hand_index += 1
                elif action in ['double', 'd'] and len(hand.cards) == 2 and player.balance >= hand.bet:
                    player.balance -= hand.bet
                    hand.bet *= 2
                    hand.has_doubled = True
                    hand.add_card(self.shoe.draw_card())
                    print(f"🃏 {hand.show()} [Value: {hand.value()}]")
                    hand.finished = True
                    hand_index += 1
                elif action in ['split', 'p'] and hand.can_split(player.balance):
                    player.balance -= hand.bet
                    # Split into two hands
                    new_hand1 = Hand(cards=[hand.cards[0]], bet=hand.bet)
                    new_hand2 = Hand(cards=[hand.cards[1]], bet=hand.bet)
                    new_hand1.add_card(self.shoe.draw_card())
                    new_hand2.add_card(self.shoe.draw_card())
                    player.hands[hand_index] = new_hand1
                    player.hands.insert(hand_index + 1, new_hand2)
                    # Do not increment hand_index: process new_hand1 next
                elif action in ['surrender', 'u'] and len(hand.cards) == 2:
                    refund = hand.bet // 2
                    player.balance += refund
                    print(f"💸 {player.name} surrenders. Half bet returned: {refund} chips.")
                    hand.bet = 0
                    hand.finished = True
                    hand_index += 1
                else:
                    print("⚠️ Invalid input.")

    def dealer_turn(self):
        print(f"\n🂠 Dealer's hand: {self.dealer.show_hand()} [Value: {self.dealer.hand.value()}]")
        while self.dealer.should_hit():  # Dealer hits until rules say stand
            self.dealer.hand.add_card(self.shoe.draw_card())
            print(f"🂡 Dealer hits: {self.dealer.show_hand()} [Value: {self.dealer.hand.value()}]")

    def resolve_round(self):
        dealer_score = self.dealer.hand.value()
        dealer_blackjack = self.dealer.hand.is_blackjack()
        print(f"\n🔚 Dealer stands at {dealer_score}")

        for player in self.players:
            for hand_index, hand in enumerate(player.hands):
                bet = hand.bet
                player_score = hand.value()
                print(f"\n💵 {player.name} - Hand {hand_index + 1}: {hand.show()} [Value: {player_score}]")

                # Insurance resolution
                if hand.insurance_bet > 0:
                    if dealer_blackjack:
                        payout = hand.insurance_bet * 2
                        player.balance += payout
                        print(f"✅ {player.name} wins insurance bet! +{payout} chips.")
                    hand.insurance_bet = 0

                # Main bet resolution
                if hand.is_blackjack() and not dealer_blackjack:
                    winnings = int(bet * 2.5)
                    player.balance += winnings
                    print(f"🎉 Blackjack! +{winnings} chips.")
                elif dealer_blackjack:
                    print("❌ Dealer has Blackjack. You lose.")
                elif player_score > 21:
                    print("💥 Busted.")
                elif dealer_score > 21 or player_score > dealer_score:
                    winnings = bet * 2
                    player.balance += winnings
                    print(f"🏆 {player.name} wins! +{winnings} chips.")
                elif player_score == dealer_score:
                    player.balance += bet
                    print("🤝 Push.")
                else:
                    print("❌ Dealer beats you.")

    def play(self):
        while True:
            self.setup_round()
            self.take_bets()
            self.deal_initial_cards()
            print(f"\n🂠 Dealer shows: {self.dealer.hand.cards[1]}")
            self.offer_insurance()

            if self.dealer.hand.is_blackjack():
                print("\n💥 Dealer has Blackjack!")
                print(f"🂠 Dealer's hand: {self.dealer.show_hand()} [Value: {self.dealer.hand.value()}]")
                self.resolve_round()
            else:
                self.player_turns()
                if any(hand.value() <= 21 for player in self.players for hand in player.hands):
                    self.dealer_turn()
                self.resolve_round()

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
