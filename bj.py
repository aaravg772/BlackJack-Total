import random
import json
from bj_bot import SimpleBlackjackAI


class Blackjack:
    def __init__(self):
        self.deck = self.create_deck()
        self.players = []
        self.ai = BlackjackAI()

    def num_player(self):
        number_of_players = int(input("Enter the number of players (1-7): "))

        while number_of_players < 1 or number_of_players > 7:
            print("Invalid number of players. Please enter a number between 1 and 7.")
            number_of_players = int(input("Enter the number of players (1-7): "))
        
        with open("data.json", "r") as file:
            data = json.load(file)
        
        data["num_players"] = number_of_players

        for i in range(1, number_of_players + 1):
            player_name = input(f"Enter the name of player {i}: ")
            while player_name in self.players:
                print("Player name already exists. Please enter a different name.")
                player_name = input(f"Enter the name of player {i}: ")
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
                "bust": 0,
                "stood": 0

            }
            self.players.append(player_name)
            print(f"Player {i} ({player_name}) has been added to the game.")
            
        
        with open("data.json", "w") as file:
            json.dump(data, file)

    def create_deck(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        deck = [(rank, suit) for suit in suits for rank in ranks]
        random.shuffle(deck)
        return deck

    def deal_card(self):
        return self.deck.pop()
    

    def calculate_score(self, player, hand):
        with open("data.json", "r") as file:   
            data = json.load(file)

        score = 0
        aces = 0

        if player == "dealer":
            for card in data["dhand"]:
                rank = card[0]

                if rank in ['Jack', 'Queen', 'King']:
                    score += 10
                elif rank == 'Ace':
                    aces += 1
                    score += 11
                else:
                    score += int(rank)
                while score > 21 and aces:
                    score -= 10
                    aces -= 1

                with open("data.json", "w") as file:
                    data["dscore"] = score
                    json.dump(data, file)
        else:
            for card in data[player]["hand"+str(hand)]:
                rank = card[0]

                if rank in ['Jack', 'Queen', 'King']:
                    score += 10
                elif rank == 'Ace':
                    aces += 1
                    score += 11
                else:
                    score += int(rank)
                while score > 21 and aces:
                    score -= 10
                    aces -= 1

                with open("data.json", "w") as file:
                    data[player]["score"+str(hand)] = score
                    json.dump(data, file)


        return score
    
    def play_game(self):
        with open("data.json", "r") as file:
            data = json.load(file)

        self.num_player()

        for player in self.players:
            data[player]["hand1"] = [self.deal_card(), self.deal_card()]
            data[player]["score1"] = self.calculate_score(player, 1)

        data["dhand"] = [self.deal_card(), self.deal_card()]
        data["dscore"] = self.calculate_score("dealer", 1)

        nat_winners = self.nat_win()
        if nat_winners:
            print(f"Natural winner(s): {', '.join(nat_winners)}")
            quit = input("Do you want to quit? (y/n): ").lower()
            if quit == 'y':
                print("Thanks for playing!")
                return
            else:
                self.play_game()
        else:
            with open("data.json", "w") as file:
                json.dump(data, file)

            for player in self.players:
                self.turns(player)
            
            self.dealer_turn()
            self.win()

    def turns (self, player):
        with open("data.json", "r") as file:
            data = json.load(file)

        turns = self.get_turns_played(player)
        turn_over = False

        if self.is_split(player):
            for turn in turns:
                if not turn:                   
                    print(f"\n{player}'s turn (split):")
                    for x in range(1, int(data[player]["hands"])+1):
                        print(f"Your hand {x+1}: {data[player]["hand"+str(x+1)]} | Score: {data[player]["score"+str(x+1)]}")
                        if data[player]["hand"+str(x)][0][0] == data[player]["hand"+str(x)][1][0] and len(data[player]["hand"+str(x)]) == 2:
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
                            while not turn_over:
                                action = input(f"Do you want to hit, stand, or end turn? (Hand {num}) (h/s): ").lower()
                                while action not in ['h', 's']:
                                    print("Invalid input. Please enter 'h' to hit or 's' to stand.")
                                    action = input(f"Do you want to hit or stand? (Hand {num}) (h/s): ").lower()
                                if action == 's':
                                    turn_over = True
                                    data[player]["stood"] = 1

                                elif action == 'h':
                                    data[player]["hand"+str(x)].append(self.deal_card())
                                    data[player][player]["score"+str(x)] = self.calculate_score(player, x)
                                    self.check_bust(player, x)
                                    print(f"Your hand {x}: {data[player]["hand"+str(x)]} | Score: {data[player]["score"+str(x)]}")
        else:
            print(f"\n{player}'s turn:")
            print(f"Your hand: {data[player]["hand1"]} | Score: {data[player]["score1"]}")

            if data["dhand"][1][0] in ['Jack', 'Queen', 'King']:
                print(f"Dealer's hand: {data["dhand"][0]} + ? | Score: {int(data["dscore"])-10} + ?")
            elif data["dhand"][1][0] == 'Ace':
                print(f"Dealer's hand: {data["dhand"][0]} + ? | Score: {int(data["dscore"])-10} + ?")
            else:
                print(f"Dealer's hand: {data["dhand"][0]} + ? | Score: {data["dscore"]-int(data["dhand"][1][0])} + ?")
            
            if data[player]["hand1"][0][0] == data[player]["hand1"][1][0]:
                print("You have a pair! You can choose to split your hand.")
                split = input("Do you want to split your hand? (y/n): ").lower()
                if split == 'y':
                    self.split(player)
                    self.turns(player)
                else:
                    print("You chose not to split your hand.")

            while not turn_over:
                action = input("Do you want to hit or stand? (h/s): ").lower()

                while action not in ['h', 's']:
                    print("Invalid input. Please enter 'h' to hit or 's' to stand.")
                    action = input("Do you want to hit or stand? (h/s): ").lower()

                if action == 'h':
                    data[player]["hand1"].append(self.deal_card())
                    data[player]["score1"] = self.calculate_score(player, 1)
                    print(f"Your hand: {data[player]["hand1"]} | Score: {data[player]["score1"]}")
                    self.check_bust(player, 1)
                    turn_over = True
                    
                elif action == 's':
                    print(f"You chose to stand. Your final hand: {data[player]["hand1"]} | Score: {data[player]["score1"]}")
                    data[player]["stood"] = 1
                    turn_over = True

        with open("data.json", "w") as file:
            json.dump(data, file)

    def dealer_turn(self):
        pass
        # not started yet

           
    def split(self, player, hand):
        with open("data.json", "r") as file:
            data = json.load(file)
        data[player]["hands"] += 1
        data[player][player]["hand"+str(hand+1)] = [data[player]["hand"+str(hand)].pop(1)]
        data[player][player]["score"+str(hand+1)] = self.calculate_score(player, hand)
        with open("data.json", "w") as file: 
            json.dump(data, file)
    
    def is_split(self, player):
        with open("data.json", "r") as file:
            data = json.load(file)

        if int(data[player]["hands"]) > 1:
            return True
        else:
            return False

            
    def win():
        with open("data.json", "r") as file:
            data = json.load(file)
    
    def nat_win(self):
        with open("data.json", "r") as file:
            data = json.load(file)

        nat_winners = []

        for player in self.players:
            if data[player]["score1"] == 21:
                nat_winners.append(player)
                data[player]["bust"] = 0
                data[player]["stood"] = 1
        
        if data["dscore"] == 21:
            nat_winners.append("dealer")
            data["dscore"] = 0
            data["bust"] = 1

        return nat_winners
        

    def get_turns_played(self, player):
        with open("data.json", "r") as file:
            data = json.load(file)

        return [data[player]["turn1"], data[player]["turn2"], data[player]["turn3"], data[player]["turn4"]]
    
    def ask_split(self, player, x):
        print("You have a pair! You can choose to split your hand.")
        split = input("Do you want to split your hand? (y/n): ").lower()
        if split == 'y':
            self.split(player, x)
            self.turns(player)
        else:
            print("You chose not to split your hand.")
    
    def check_bust(self, player, hand):
        with open("data.json", "r") as file:
            data = json.load(file)
        
        data[player]["score"] = self.calculate_score(player, hand)

        if data[player]["score"+str(hand)] > 21:
            data[player]["bust"] = 1
            with open("data.json", "w") as file:
                json.dump(data, file)
            print(f"{player} busted! Your final hand: {data[player]["hand"+str(hand)]} | Score: {data[player]["score"+str(hand)]}")
            data.pop(player)
            with open("data.json", "w") as file:
                json.dump(data, file)
            player_index = self.players.index(player)
            if player_index == len(self.players) - 1:
                self.players.pop(player_index)
                self.dealer_turn()
            else:
                self.players.pop(player_index)
                self.turns(self.players[player_index])
        else:
            pass
