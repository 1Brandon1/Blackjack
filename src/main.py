from game import Game

def printTitle():
    print("""
  ==============================
           🂡 BLACKJACK 🂡
       Beat the Dealer & Win!
  ==============================
    """)

def getNumPlayers():
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

def getPlayerNames(numPlayers):
    names = []
    for i in range(numPlayers):
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
    printTitle()
    numPlayers = getNumPlayers()
    playerNames = getPlayerNames(numPlayers)

    game = Game(playerNames)
    game.play()

if __name__ == "__main__":
    main()