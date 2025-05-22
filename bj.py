import random
import json


class Blackjack:
    def __init__(self):
        self.deck = self.create_deck()
        self.players = []

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
            data[player_name] = {
                "hand": (),
                "score": 0,
                "split": False
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
    

    def calculate_score(self, hand):
        score = 0
        aces = 0

        for card in hand:
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

        return score
    
    def play_game(self):
        with open("data.json", "r") as file:
            data = json.load(file)

        self.num_player()

        for player in self.players:
            data[player]["hand"] = [self.deal_card(), self.deal_card()]
            data[player]["score"] = self.calculate_score(data[player]["hand"])

        data["dhand"] = [self.deal_card(), self.deal_card()]
        data["dscore"] = self.calculate_score(data["dhand"])

        for player in self.players:
            self.turns(player)
            self.win()

    def turns (self, player, splitnum=0):
        with open("data.json", "r") as file:
            data = json.load(file)

        if self.is_split(player):
            if splitnum == 1:
                print(f"\n{player}'s turn (split):")
                print(f"Your hand 1: {data[player+"1"]["hand"]} | Score: {data[player+"1"]["score"]}")
                print(f"Your hand 2: {data[player+"2"]["hand"]} | Score: {data[player+"2"]["score"]}")
                if data[player+"1"]["hand"][1][0] == data[player+"1"]["hand"][1][0]:
                    print("You have a pair! You can choose to split your hand.")
                    split = input("Do you want to split your hand? (y/n): ").lower()
                    if split == 'y':
                        self.split(player+"1")
                        self.turns(player, 2)
                    else:
                        print("You chose not to split your hand.")

                elif data[player+"2"]["hand"][1][0] == data[player+"2"]["hand"][1][0]:
                    print("You have a pair! You can choose to split your hand.")
                    split = input("Do you want to split your hand? (y/n): ").lower()
                    if split == 'y':
                        self.split(player+"2")
                        self.turns(player, 2)
                    else:
                        print("You chose not to split your hand.")
                        
                else:
                    action = input("Do you want to hit or stand? (Hand One) (h/s): ").lower()
                    while action not in ['h', 's']:
                        print("Invalid input. Please enter 'h' to hit or 's' to stand.")
                        action = input("Do you want to hit or stand? (Hand One) (h/s): ").lower()
                    if action == 'h':
                        data[player][player+"1"]["hand"].append(self.deal_card())
                        data[player][player+"1"]["score"] = self.calculate_score(data[player][player+"1"]["hand"])
                        print(f"Your hand 1: {data[player][player+"1"]["hand"]} | Score: {data[player][player+"1"]["score"]}")
                        self.win()


        print(f"\n{player}'s turn:")
        print(f"Your hand: {data[player]["hand"]} | Score: {data[player]["score"]}")

        if data["dhand"][1][0] in ['Jack', 'Queen', 'King']:
            print(f"Dealer's hand: {data["dhand"][0]} + ? | Score: {int(data["dscore"])-10} + ?")
        elif data["dhand"][1][0] == 'Ace':
            print(f"Dealer's hand: {data["dhand"][0]} + ? | Score: {int(data["dscore"])-10} + ?")
        else:
            print(f"Dealer's hand: {data["dhand"][0]} + ? | Score: {data["dscore"]-int(data["dhand"][0][1])} + ?")
        
        if data[player][0][0] == data[player][1][0]:
            print("You have a pair! You can choose to split your hand.")
            split = input("Do you want to split your hand? (y/n): ").lower()
            if split == 'y':
                self.split(player)
                self.turns(player, 1)
            else:
                print("You chose not to split your hand.")

        action = input("Do you want to hit or stand? (h/s): ").lower()

        while action not in ['h', 's']:
            print("Invalid input. Please enter 'h' to hit or 's' to stand.")
            action = input("Do you want to hit or stand? (h/s): ").lower()

        if action == 'h':
            data[player]["hand"].append(self.deal_card())
            data[player]["score"] = self.calculate_score(data[player]["hand"])
            print(f"Your hand: {data[player]["hand"]} | Score: {data[player]["score"]}")
            self.win()
            
        elif action == 's':
            print(f"You chose to stand. Your final hand: {data[player]["hand"]} | Score: {data[player]["score"]}")
            self.win()

    def dealer_turn(self):
        # to be continued
        pass
           
    def split(self, player):
        with open("data.json", "r") as file:
            data = json.load(file)
        data[player]["split"] = True
        data[player][player+"1"]["hand"] = [data[player]["hand"].pop(0)]
        data[player][player+"2"]["hand"] = [data[player]["hand"].pop(1)]
        data[player][player+"1"]["score"] = self.calculate_score(data[player][player+"1"]["hand"])
        data[player][player+"2"]["score"] = self.calculate_score(data[player][player+"2"]["hand"])
        data[player].pop("hand")
        data[player].pop("score")

        with open("data.json", "w") as file:
            json.dump(data, file)
    
    def is_split(self, player):
        with open("data.json", "r") as file:
            data = json.load(file)

        if data[player]["split"] == True:
            return True
        else:
            return False

            
    def win():
        with open("data.json", "r") as file:
            data = json.load(file)

        

