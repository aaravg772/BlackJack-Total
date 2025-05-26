
import random
import json
import time

# Path To Database (JSON file)
FILE = "data.json"

# Define the Blackjack class
class Blackjack:
    def __init__(self):
        # Aarav
        """Initialize the Blackjack game."""

        self.deck = self.create_deck()
        self.players = []

    def num_player(self):
        # Aarav
        """Initializing the player data in a JSON file."""

        # Ask the user for the number of players
        number_of_players = int(input("Enter the number of players (1-7): "))

        # Keep asking until a valid number is entered
        while number_of_players < 1 or number_of_players > 7:
            print("Invalid number of players. Please enter a number between 1 and 7.")
            number_of_players = int(input("Enter the number of players (1-7): "))

        data = self.get_data()
        
        data["num_players"] = number_of_players

        for i in range(number_of_players):
            # Ask for player name and ensure it's not repeated
            player_name = input(f"Enter the name of player {i}: ")
            while player_name in self.players:
                print("Player name already exists. Please enter a different name.")
                player_name = input(f"Enter the name of player {i}: ")
            # Add player data to the data
            data[player_name] = {
                "hand1": [],
                "hand2": [],
                "hand3": [],
                "hand4": [],
                "score1": 0,
                "score2": 0,
                "score3": 0,
                "score4": 0,
                "turn1": 0,
                "turn2": 0,
                "turn3": 0,
                "turn4": 0,
                "hands": 1,
                "bust1": 0,
                "bust2": 0, 
                "bust3": 0,
                "bust4": 0,
                "stood": 0
            }
            self.players.append(player_name)
            print(f"Player {i} ({player_name}) has been added to the game.")
            
        # Initialize dealer data in the JSON file
        with open(FILE, "w") as file:
            json.dump(data, file, indent=4)

    def create_deck(self):
        # Aarav
        """Create a standard deck of 52 playing cards, shuffle it, and return the deck."""
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        deck = [[rank, suit] for suit in suits for rank in ranks]
        random.shuffle(deck)
        random.shuffle(deck)
        random.shuffle(deck)
        return deck

    def deal_card(self):
        # Aarav
        """Deal a card from the deck."""

        return self.deck.pop()
    

    def calculate_score(self, player, hand):
        # Artin
        """Calculate the score for a given player and hand."""

        data = self.get_data()

        score = []
        aces = 0
        
        # If the player is the dealer, calculate the score for the dealer's hand
        if player == "dealer":
            for card in data["dhand"]:
                # Handle face cards and Aces
                if card[0] in ['Jack', 'Queen', 'King']:
                    # Jack, Queen, King are worth 10 points
                    score.append(10)
                elif card[0] == 'Ace':
                    # Ace is worth 11 points, but can be adjusted to 1 point if necessary
                    score.append(11)
                    aces += 1
                else:
                    # Number cards are worth their face value
                    score.append(int(card[0]))

            total = sum(score)

            # Adjust for Aces if total exceeds 21
            while total > 21 and aces > 0:
                total -= 10
                aces -= 1

            # Update the dealer's score in the data
            data["dscore"] = total

        # If the player is not the dealer, calculate the score for the player's hand
        else:
            # Finidung the player's hand and calculating the score
            for card in data[player]["hand"+str(hand)]:
                # Handle face cards and Aces
                if card[0] in ['Jack', 'Queen', 'King']:
                    # Jack, Queen, King are worth 10 points
                    score.append(10)
                elif card[0] == 'Ace':
                    # Ace is worth 11 points, but can be adjusted to 1 point if necessary
                    score.append(11)
                    aces += 1
                else:
                    # Number cards are worth their face value
                    score.append(int(card[0]))

            total = sum(score)

            # Adjust for Aces if total exceeds 21
            while total > 21 and aces > 0:
                total -= 10
                aces -= 1

            # Update the player's score in the data
            data[player]["score"+str(hand)] = total

        # Update the data in the JSON file
        with open(FILE, "w") as file:
            json.dump(data, file, indent=4)

        # Return the total score
        return total

    
    def play_game(self):
        # Aarav
        """The main Blackjack game function, to start the game and manage the turns."""

        # Initialize the game by setting up the players and dealing initial cards
        self.num_player()
        data = self.get_data()

        for player in self.players:
            data[player]['hand1'] = [self.deal_card(), self.deal_card()]
            data[player]["score1"] = self.calculate_score(player, 1)

        data["dhand"] = [self.deal_card(), self.deal_card()]
        
        with open(FILE, "w") as file:
            json.dump(data, file, indent=4)

        self.calculate_score("dealer", 1)

        # Check for natural winners (blackjack) before proceeding with turns
        nat_winners = self.nat_win()

        # If there are natural winners, print their results and end the game
        if nat_winners:
            print(f"Natural winner(s): {', '.join(nat_winners)}")
            for player in nat_winners:
                if player == "dealer":print(f"{player} wins with a natural blackjack! With Hand: {data['dhand']} | Score: {data['dscore']}")
                else:print(f"{player} wins with a natural blackjack! With Hand: {data[player]['hand1']} | Score: {data[player]['score1']}")

        # If there are no natural winners, proceed with the game
        else:
            for player in self.players:
                self.turns(player)
            
            self.dealer_turn()
            self.win()

    def turns (self, player):
        # Aarav
        """Manage the turns for each player, allowing them to hit, stand, or split their hand."""

        # Initialize the player's turn with data and the needed variables
        data = self.get_data()

        turns = self.get_turns_played(player)
        turn_over = False

        if self.is_split(player):
            # If the player has split their hand in the past, handle each hand separately
            for turn in turns:
                if not turn:                   
                    print(f"\n{player}'s turn (split):")
                    for x in range(1, int(data[player]["hands"])+1):
                        # Loop through each hand and manage the player's actions
                        self.calculate_score(player, x)
                        data = self.get_data()
                        print(f"Your hand {x+1}: {data[player]['hand'+str(x+1)]} | Score: {data[player]['score'+str(x)]}")
                        # Check if the player has a pair and can split, if so, ask to split
                        if data[player]['hand'+str(x)][0][0] == data[player]['hand'+str(x)][1][0] and len(data[player]['hand'+str(x)]) == 2 and data[player]["hands"] < 4:
                            self.ask_split(player, x)            
                        else:
                            num = None
                            if x == 1:
                                num = "One"
                            elif x == 2:
                                num = "Two"
                            elif x == 3:
                                num = "Three"
                            elif x == 4:
                                num = "Four"

                            # Loop until the player decides to stand
                            while not turn_over:

                                # Ask the player for their action (hit or stand)
                                action = input(f"Do you want to hit or stand? (Hand {num}) (h/s): ").lower()

                                # Keep asking untile the input is for hit or stand
                                while action not in ['h', 's']:
                                    print("Invalid input. Please enter 'h' to hit or 's' to stand.")
                                    action = input(f"Do you want to hit or stand? (Hand {num}) (h/s): ").lower()

                                # If the player chooses to stand, the turn is over
                                if action == 's':
                                    turn_over = True
                                    data[player]["stood"] = 1

                                # If the player chooses to hit, deal a card and update the score
                                elif action == 'h':
                                    data[player]["hand"+str(x)].append(self.deal_card())
                                    with open(FILE, "w") as file:
                                        json.dump(data, file, indent=4)
                                    self.calculate_score(player, x)  
                                    self.check_bust(player, x)
                                    data = self.get_data()
                                    if data[player]["bust"] == 1:
                                        return
                                    print(f"Your hand {x}: {data[player]['hand'+str(x)]} | Score: {data[player]['score'+str(x)]}")
                                    
        # If the player does not have a split hand, handle their turn normally
        else:

            # Initialize the player's turn by prtinting their hand and score and getting important data and variables
            print(f"\n{player}'s turn:")
            self.calculate_score(player, 1)
            data = self.get_data()
            print(f"Your hand: {data[player]['hand1']} | Score: {data[player]['score1']}")

            print(f"Dealer's hand: {data['dhand'][0]} + ? | Score: ?")
            
            # Check if the player has a pair and can split, if so, ask to split
            if data[player]["hand1"][0][0] == data[player]["hand1"][1][0]:
                print("You have a pair! You can choose to split your hand.")
                split = input("Do you want to split your hand? (y/n): ").lower()
                if split == 'y':
                    self.split(player)
                    self.turns(player)
                else:
                    print("You chose not to split your hand.")
                
            # Loop until the player decides to stand
            while not turn_over:
                action = input("Do you want to hit or stand? (h/s): ").lower()

                # Keep asking untile the input is for hit or stand
                while action not in ['h', 's']:
                    print("Invalid input. Please enter 'h' to hit or 's' to stand.")
                    action = input("Do you want to hit or stand? (h/s): ").lower()

                # If the player chooses to hit, deal a card and update the score
                if action == 'h':
                    data[player]["hand1"].append(self.deal_card())
                    with open(FILE, "w") as file:
                        json.dump(data, file, indent=4)
                    self.calculate_score(player, 1)
                    self.check_bust(player, 1)
                    data = self.get_data()
                    if data[player]["bust"] == 1:
                        return
                    print(f"Your hand: {data[player]['hand1']} | Score: {data[player]['score1']}")
                    
                # If the player chooses to stand, the turn is over    
                elif action == 's':
                    self.calculate_score(player, 1)
                    data = self.get_data()
                    print(f"You chose to stand. Your final hand: {data[player]['hand1']} | Score: {data[player]['score1']}")
                    data[player]["stood"] = 1
                    turn_over = True

        # Update the player's turn data in the JSON file
        with open(FILE, "w") as file:
            json.dump(data, file, indent=4)


    def dealer_turn(self):
        # Artin
        """Manage the dealer's turn, making sure they hit until their score is at least 17."""

        dealer_score = self.calculate_score("dealer", 1)
        while dealer_score < 17:
            data = self.get_data()
            data["dhand"].append(self.deal_card())
            with open(FILE, "w") as file:
                json.dump(data, file, indent=4)
            dealer_score = self.calculate_score("dealer", 1)
            self.check_bust("dealer", 1)      
            time.sleep(.1)

           
    def split(self, player, hand):
        # Aarav
        """Split the player's hand into two separate hands if they have a pair."""
        data = self.get_data()

        data[player]["hands"] += 1
        data[player]["hand"+str(hand+1)] = [data[player]["hand"+str(hand)].pop(1)]

        with open(FILE, "w") as file: 
            json.dump(data, file, indent=4)

        self.calculate_score(player, hand)
    
    def is_split(self, player):
        # Aarav
        """Check if the player has split their hand in the past."""
        data = self.get_data()

        if int(data[player]["hands"]) > 1:
            return True
        else:
            return False

            
    def win(self):
        # Artin
        """Determine the winners of the game based on the final scores of each player and the dealer."""

        data = self.get_data()

        # Make a dictionary to store the winners of each hand for each player.
        winners = {

        }

        # Initialize the winners dictionary for each player and their hands
        for player in self.players:
            winners[player] = {}
            for x in range(1, int(data[player]["hands"])+1):
                winners[player]["hand"+str(x)] = 0

        # Check each player's each hand's score against the dealer's score and determine the outcome
        for player in self.players:
            for x in range(1, int(data[player]["hands"])+1):
                if data["dbust"] == 1:
                    # Win
                    winners[player]["hand"+str(x)] = 1
                if data[player]["score"+str(x)] > data["dscore"] and data[player]["bust"] == 0:
                    # Win
                    winners[player]["hand"+str(x)] = 1
                elif data[player]["score"+str(x)] < data["dscore"] and data["dscore"] < 22:
                    # Loss
                    winners[player]["hand"+str(x)] = 0
                elif data[player]["score"+str(x)] == data["dscore"]:
                    # Tie
                    winners[player]["hand"+str(x)] = .5

        # Print the outcome of the game
        print(f"\nDealer's hand: {data['dhand']} | Score: {data['dscore']}")
        for person, result in winners.items():
            for hand, outcome in result.items():
                if outcome == 1:
                    print(f"{person} wins with Hand {hand[4]}!")
                elif outcome == 0:
                    print(f"{person} loses with hand {hand[4]}.")
                elif outcome == .5:
                    print(f"{person} ties with hand {hand[4]}.")

        self.reset_game()
        

    def nat_win(self):
        # Aarav
        """Check for natural winners (blackjack) at the start of the game."""

        data = self.get_data()

        nat_winners = []

        # Check if any player has a natural blackjack (21 with two cards)
        for player in self.players:
            if data[player]["score1"] == 21 and len(data[player]["hand1"]) == 2:
                nat_winners.append(player)
                data[player]["bust"] = 0
                data[player]["stood"] = 1

        # Check if the dealer has a natural blackjack
        if data["dscore"] == 21:
            nat_winners.append("dealer")
            data["dscore"] = 0
            data["bust"] = 1


        return nat_winners
        

    def get_turns_played(self, player):
        # Aarav
        """Get the number of turns played by a player."""

        data = self.get_data()

        return [data[player]["turn1"], data[player]["turn2"], data[player]["turn3"], data[player]["turn4"]]
    
    def ask_split(self, player, x):
        # Aarav
        """Ask the player if they want to split their hand if they have a pair."""

        print("You have a pair! You can choose to split your hand.")
        split = input("Do you want to split your hand? (y/n): ").lower()
        if split == 'y':
            self.split(player, x)
            self.turns(player)
        else:
            print("You chose not to split your hand.")
    
    def check_bust(self, player, hand):
        # Aarav
        """Check if a player or the dealer has busted (exceeded a score of 21)."""
        self.calculate_score(player, hand)
        data = self.get_data()

        # If the player is the dealer, check if the dealer has busted
        if player == "dealer":
            if data["dscore"] > 21:
                data["dbust"] = 1
                with open(FILE, "w") as file:
                    json.dump(data, file, indent=4)
                return
            
        # If the player is not the dealer, check if the player has busted
        else:
            if data[player]["score"+str(hand)] > 21:
                data[player]["bust"] = 1
                with open(FILE, "w") as file:
                    json.dump(data, file, indent=4)
                print(f"{player} busted! Your final hand: {data[player]['hand'+str(hand)]} | Score: {data[player]['score'+str(hand)]}")

                # If the player has busted, remove them from the game and end their turn
                player_index = self.players.index(player)
                if player_index == len(self.players) - 1:
                    self.players.pop(player_index)
                    self.dealer_turn()
                else:
                    self.players.pop(player_index)
                    self.turns(self.players[player_index])
            else:
                pass

    def reset_game(self):
        # Aarav
        """Reset the game data in the JSON file to start a new game."""
        with open(FILE, "w") as file:
            json.dump({
                "num_players": 0,
                "dhand": [],
                "dscore": 0,
                "dbust": 0
            }, file, indent=4)
        print("Game has been reset. You can start a new game.")

    def get_data(self):
        # Aarav
        """Function to retrieve the game data from the JSON file."""
        with open(FILE, "r") as file:
            data = json.load(file)
            return data

game = Blackjack()
game.play_game()
