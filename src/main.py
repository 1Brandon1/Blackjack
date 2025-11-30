from game import Game


def print_title():
    print("""
  ==============================
           🂡 BLACKJACK 🂡
       Beat the Dealer & Win!
  ==============================
    """)


def get_num_players():
    while True:
        try:
            num = int(input("👥 Enter number of players (1–7): "))
            if 1 <= num <= 7:
                return num
            print("⚠️ Please enter a number between 1 and 7.")
        except ValueError:
            print("⚠️ Invalid input. Please enter a number.")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Exiting game.")
            exit()


def get_player_names(num_players):
    names = []
    for i in range(num_players):
        try:
            name = input(f"🧑 Enter name for player {i + 1}: ").strip()
            if not name:
                name = f"Player{i + 1}"
            names.append(name)
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Exiting game.")
            exit()
    print()
    return names


def main():
    print_title()
    num_players = get_num_players()
    player_names = get_player_names(num_players)

    game = Game(player_names)
    game.play()


if __name__ == "__main__":
    main()
