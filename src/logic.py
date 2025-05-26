import json
import random
import os

# Path To Database (JSON file)
# Using a relative path for better portability
FILE = "data.json"

class BlackjackLogic:

    """
    Purely logic class for Blackjack game.
    Manages game state, rules, and core mechanics.
    """

    def __init__(self, data_file=FILE):
        self.data_file = data_file
        self.deck = self.create_deck()
        self.players = []  # List of player names
        self._initialize_game_data() # Ensure data.json exists and is initialized

    def _initialize_game_data(self):

        """Initializes the data.json file if it doesn't exist or is empty."""

        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) == 0:
            self.reset_game_data() # Use a dedicated reset method for clarity
        else:
            # Validate existing data
            try:
                data = self.get_data()
                # Basic validation: ensure essential keys exist
                if "num_players" not in data or "dhand" not in data or "dscore" not in data or "dbust" not in data or "players_data" not in data:
                    self.reset_game_data()
            except:
                # If file is corrupt or invalid, reset it
                self.reset_game_data()

    def reset_game_data(self):
        """Resets the game data in the JSON file to its initial state."""
        initial_data = {
            "num_players": 0,
            "dhand": [],
            "dscore": 0,
            "dbust": 0,
            "players_data": {} # Store player-specific data here
        }
        with open(self.data_file, "w") as file:
            json.dump(initial_data, file, indent=4)
        self.players = [] # Clear internal players list as well

    def get_data(self):
        """Retrieves the game data from the JSON file."""
        with open(self.data_file, "r") as file:
            return json.load(file)

    def _save_data(self, data):
        """Saves the current game data to the JSON file."""
        with open(self.data_file, "w") as file:
            json.dump(data, file, indent=4)

    def create_deck(self):
        """Creates a standard deck of 52 playing cards and shuffles it."""
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        deck = [[rank, suit] for suit in suits for rank in ranks]
        random.shuffle(deck)
        random.shuffle(deck)
        random.shuffle(deck)
        return deck

    def deal_card(self):
        """Deals a card from the deck."""
        return self.deck.pop()

    def add_player(self, player_name):
        """Adds a new player to the game data."""
        data = self.get_data()

        data["players_data"][player_name] = {
            "hand1": [],
            "hand2": [],
            "hand3": [],
            "hand4": [],
            "score1": 0,
            "score2": 0,
            "score3": 0,
            "score4": 0,
            "turn1": 0, # Tracks if turn for hand 1 is played
            "turn2": 0,
            "turn3": 0,
            "turn4": 0,
            "stood1": 0,
            "stood2": 0,
            "stood3": 0,
            "stood4": 0,
            "bust1": 0,
            "bust2": 0, 
            "bust3": 0,
            "bust4": 0,
            "hands": 1, # Number of active hands for this player
            "bust": 0,  # 1 if busted, 0 otherwise
            "stood": 0  # 1 if stood, 0 otherwise
        }
        data["num_players"] += 1
        self.players.append(player_name)
        self._save_data(data)

    def calculate_score(self, name, hand_number=1):

        """
        Calculates the score for a given entity (player or dealer) and hand.
        `hand_number` is only relevant for players with split hands.
        """

        data = self.get_data()
        score_list = []
        aces = 0
        current_hand = []

        if name == "dealer":
            current_hand = data["dhand"]
        else:
            hand_key = f"hand{hand_number}"
            current_hand = data["players_data"][name][hand_key]

        for card in current_hand:
            rank = card[0]
            if rank in ['Jack', 'Queen', 'King']:
                score_list.append(10)
            elif rank == 'Ace':
                score_list.append(11)
                aces += 1
            else:
                score_list.append(int(rank))

        total_score = sum(score_list)

        # Adjust for Aces if total exceeds 21
        while total_score > 21 and aces > 0:
            total_score -= 10
            aces -= 1

        # Update the score in the data
        if name == "dealer":
            data["dscore"] = total_score
        else:
            data["players_data"][name][f"score{hand_number}"] = total_score




        self._save_data(data)
        return total_score

    def initial_deal(self):

        """Deals initial two cards to all players and the dealer."""

        data = self.get_data()
        for player in self.players:
            player_data = data["players_data"][player]
            player_data['hand1'] = [self.deal_card(), self.deal_card()]
            data["players_data"][player] = player_data # Update player data
            self._save_data(data) 
            player_data["score1"] = self.calculate_score(player, 1)

        data["dhand"] = [self.deal_card(), self.deal_card()]
        self._save_data(data)
        self.calculate_score("dealer")

    def get_hand_details(self, name, hand_number=1):

        """Returns the hand and score for a given entity and hand number."""

        data = self.get_data()
        if name == "dealer":
            return data["dhand"], data["dscore"]
        else:
            player_data = data["players_data"][name]
            self.calculate_score(name, hand_number) # Ensure score is up-to-date
            hand_key = f"hand{hand_number}"
            score_key = f"score{hand_number}"
            return player_data[hand_key], player_data[score_key]

    def check_natural_winners(self):

        """Checks for natural blackjacks at the start of the game."""

        data = self.get_data()
        nat_winners = []

        for player_name in self.players:
            player_data = data["players_data"][player_name]

            if player_data["score1"] == 21 and len(player_data["hand1"]) == 2:
                nat_winners.append(player_name)
                player_data["stood"] = 1 # Player with natural blackjack stands
                player_data["bust"] = 0 # Cannot bust with natural blackjack
                data["players_data"][player_name] = player_data # Update player data

        # Dealer natural blackjack trumps player natural blackjack in many rulesets
        if data["dscore"] == 21 and len(data["dhand"]) == 2:
            nat_winners.append("dealer")
            # If dealer has natural, all players with natural tie, others lose
            # For simplicity here, we just report dealer as winner
            # More complex rules would involve comparing player naturals to dealer natural
            data["dbust"] = 0 # Dealer cannot bust with natural
            data["dscore"] = 21 # Ensure score is correctly set (was set to 0 in original code if dealer nat)

        self._save_data(data) # Save stood/bust status for players
        return nat_winners

    def player_hit(self, player_name, hand_number=1):

        """Player takes another card. Returns True if successful, False if busted."""

        data = self.get_data()
        hand_key = f"hand{hand_number}"
        score_key = f"score{hand_number}"
        player_data = data["players_data"][player_name]

        if player_data["bust"] == 1 or player_data["stood"] == 1:
            return False # Player not found, already busted, or already stood

        player_data[hand_key].append(self.deal_card())
        self._save_data(data) # Save updated hand before recalculating score

        self.calculate_score(player_name, hand_number)

        return True

    def player_stand(self, player_name):

        """Player chooses to stand."""

        data = self.get_data()
        data["players_data"][player_name]["stood"] = 1
        self._save_data(data)
        return True
    
        return False

    def is_player_busted(self, player_name, hand_number=1):

        """Checks if a player's specific hand has busted."""

        data = self.get_data()
        player_data = data["players_data"][player_name]

  
        if player_data[f"score{hand_number}"] > 21:
            player_data[f"bust{hand_number}"] = 1
            data["players_data"][player_name] = player_data
            self._save_data(data)

        if player_data[f"bust{hand_number}"] == 1:
            return True or player_data["bust"] == 1
        
        return False # Player has not busted for this hand
            
        


    def is_player_stood(self, player_name):

        """Checks if a player has stood for all their hands."""

        data = self.get_data()
        player_data = data["players_data"][player_name]
        # If a player has multiple hands, they 'stood' when all hands are resolved (stood or busted)
        # For simplicity, if 'stood' is marked, assume they've completed their turn.
        return player_data["stood"] == 1 or player_data["bust"] == 1

    def dealer_turn(self):

        """Dealer hits until their score is 17 or higher, or busts."""

        data = self.get_data()
        dealer_score = data["dscore"] # Get current score

        while dealer_score < 17:
            data["dhand"].append(self.deal_card())
            self._save_data(data) # Save after adding card
            dealer_score = self.calculate_score("dealer") # Recalculate score

        self.is_dealer_busted() # Check if dealer busted
        self._save_data(data) # Save final state

    def can_split(self, player_name, hand_number=1):

        """Checks if a player can split their hand."""

        data = self.get_data()
        player_data = data["players_data"][player_name]
        hand_key = f"hand{hand_number}"
        current_hand = player_data[hand_key]

        # Can only split if two cards and ranks are the same
        return (current_hand and
                len(current_hand) == 2 and
                player_data["hands"] < 4 and # Max 4 hands after splitting
                current_hand[0][0] == current_hand[1][0])

    def split_hand(self, player_name, hand_number):

        """Splits the player's hand into two separate hands."""

        data = self.get_data()
        player_data = data["players_data"][player_name]

        # Get the card to move to the new hand
        card_to_move = player_data[f"hand{hand_number}"][0].pop()

        # Increment the number of hands
        player_data["hands"] += 1
        new_hand_number = player_data["hands"]

        player_data[f"hand{new_hand_number}"].append(card_to_move)

        self._save_data(data) # Save changes
        # Recalculate scores for both hands after split
        self.calculate_score(player_name, hand_number)
        self.calculate_score(player_name, new_hand_number)


    def get_game_results(self):

        """
        Determines the winners of the game based on final scores.
        Returns a dictionary of player_name -> {hand_number -> outcome}.
        Outcome: 1 (win), 0 (loss), 0.5 (tie).
        """

        data = self.get_data()
        dealer_score = data["dscore"]
        dealer_busted = data["dbust"] == 1
        results = {}

        for player_name in self.players:
            player_results = {}
            player_data = data["players_data"][player_name]
            num_hands = player_data["hands"]

            if player_data["bust"] == 1:
                for i in range(1, num_hands + 1):
                    player_results[i] = 0
            
            else:

                for i in range(1, num_hands + 1):
                    player_hand_score = player_data[f"score{i}"]
                    player_busted = player_data[f"bust{i}"] == 1

                    if player_busted:
                        player_results[i] = 0 # Player busted, always a loss for this hand
                    elif dealer_busted:
                        player_results[i] = 1 # Dealer busted, player wins (if not busted)
                    elif player_hand_score > dealer_score:
                        player_results[i] = 1 # Player has higher score, wins
                    elif player_hand_score < dealer_score:
                        player_results[i] = 0 # Player has lower score, loses
                    else: # Scores are equal
                        player_results[i] = 0.5 # Tie

            results[player_name] = player_results

        return results

    def get_all_player_names(self):

        """Returns a list of all current player names."""

        return list(self.players) # Return a copy to prevent external modification

    def get_num_hands(self, player_name):

        """Returns the number of active hands a player has."""

        data = self.get_data()
        player_data = data["players_data"][player_name]

        return player_data["hands"]


    def set_turn_played(self, player_name, hand_number):

        """Marks a specific hand's turn as played for a player."""

        data = self.get_data()
        player_data = data["players_data"][player_name]

        player_data[f"turn{hand_number}"] = 1
        self._save_data(data)

    def is_turn_played(self, player_name, hand_number):

        """Checks if a specific hand's turn has been played for a player."""

        data = self.get_data()
        player_data = data["players_data"][player_name]

        return player_data.get(f"turn{hand_number}") == 1

    def get_overall_player_status(self, player_name):

        """Returns the overall status of a player (e.g., 'bust', 'stood', 'active')."""

        data = self.get_data()
        player_data = data["players_data"][player_name]
        hands = player_data["hands"]
        bust = []

        for x in range(1, hands + 1):
            if player_data[f"bust{x}"] == 1:
                bust.append(True)
            else:
                bust.append(False)
        


        if player_data["bust"] or False not in bust:
            return "busted"
        if player_data["stood"] == 1:
            return "stood"
        
        return "active"

    def is_dealer_busted(self):

        """Checks if the dealer has busted."""

        data = self.get_data()

        if data["dscore"] > 21:
            data["dbust"] = 1
            self._save_data(data)
            return True
        
        return data["dbust"] == 1
    
