import random
import json
import time
import os
from logic import BlackjackLogic


class BlackjackGame:

    """
    Text-based interface for the Blackjack game.
    Uses the BlackjackLogic class to manage game.
    """

    def __init__(self):
        self.logic = BlackjackLogic()

    def _get_player_input(self, prompt, valid_options=None):

        """Helper to get validated input from the user."""

        while True:
            user_input = input(prompt).strip().lower()
            if valid_options and user_input not in valid_options:
                print(f"Invalid input. Please enter one of: {', '.join(valid_options)}.")
            else:
                return user_input

    def setup_players(self):

        """Prompts for and adds players to the game."""

        number_of_players = int(self._get_player_input("Enter the number of players (1-7): ", ["1", "2", "3", "4", "5", "6", "7"]))
                
        self.logic.reset_game_data() # Ensure fresh start
        print("Game reset for new players.")

        added_count = 0

        while added_count < number_of_players:
            player_name = input(f"Enter the name of player {added_count + 1}: ").strip()
            if not player_name:
                print("Player name cannot be empty.")
                continue
            elif player_name in self.logic.get_all_player_names():
                print("Player name already exists. Please enter a different name.")
                continue
            else: 
                self.logic.add_player(player_name)
                print(f"Player {added_count + 1} ({player_name}) has been added to the game.")
                added_count += 1

    def display_hand(self, name, hand, score):

        """Prints a hand and score."""

        if name == "dealer" and len(hand) == 2:
            print(f"Dealer's hand: {hand[0]} + ? | Score: ?")
        else:
            print(f"{name}'s hand: {hand} | Score: {score}")

    def player_turn(self, player_name):

        """Manages a single player's turn, including potential splits."""

        print(f"\n--- {player_name}'s Turn ---")
        player_status = self.logic.get_overall_player_status(player_name)

        if player_status == "busted":
            print(f"{player_name} already busted.")
            return
        if player_status == "stood":
            print(f"{player_name} already stood.")
            return

        num_hands = self.logic.get_num_hands(player_name)

        for i in range(1, num_hands + 1):
            if self.logic.is_turn_played(player_name, i):
                continue

            hand, score = self.logic.get_hand_details(player_name, i)
            self.display_hand(player_name, hand, score)
            dealer_hand, _ = self.logic.get_hand_details("dealer")
            self.display_hand("dealer", dealer_hand, 0)

            if self.logic.is_player_busted(player_name, i):
                print(f"{player_name}, Hand {i} busted with score {score}.")
                self.logic.set_turn_played(player_name, i)
                continue

            if self.logic.can_split(player_name, i):
                split_choice = self._get_player_input("You have a pair! Do you want to split this hand? (y/n): ", ['y', 'n'])
                if split_choice == 'y':
                    if self.logic.split_hand(player_name, i):
                        print(f"Hand {i} split. You now have {self.logic.get_num_hands(player_name)} hands.")
                        self.player_turn(player_name)
                        return

            turn_over = False
            while not turn_over:
                action = self._get_player_input(f"Hand {i}: Do you want to hit or stand? (h/s): ", ['h', 's'])

                if action == 'h':
                    if self.logic.player_hit(player_name, i):
                        hand, score = self.logic.get_hand_details(player_name, i)
                        self.display_hand(player_name, hand, score)
                        if self.logic.is_player_busted(player_name, i):
                            self.logic.get_hand_details(player_name, i) # Mark this hand's turn as played
                            print(f"{player_name}, busted with Hand {i}: {hand} with score {score}.")
                            turn_over = True
                    else:
                        print(f"Error occurred.")
                        turn_over = True
                elif action == 's':
                    hand, score = self.logic.get_hand_details(player_name, i)

                    print(f"You chose to stand on Hand {i}. Your final hand: {hand} | Score: {score}")
                    turn_over = True # End turn for this hand

            self.logic.set_turn_played(player_name, i) # Mark this hand's turn as played


    def play_game(self):

        """Main game loop for the text-based Blackjack."""

        self.setup_players()
        self.logic.initial_deal()

        print("\n--- Initial Deal ---")

        natural_winners = self.logic.check_natural_winners()
        if natural_winners:
            print("\n--- Natural Blackjacks! ---")
            for winner in natural_winners:
                hand, score = self.logic.get_hand_details(winner)
                print(f"{winner} wins with a natural blackjack! Hand: {hand} | Score: {score}")

            print("Game ends due to natural blackjacks.")
            self.logic.reset_game_data() # Reset for a new game
            return

        # Player turns
        for player_name in self.logic.get_all_player_names():
            if self.logic.get_overall_player_status(player_name) not in ["busted", "stood"]:
                self.player_turn(player_name)

        # Dealer's turn
        print("\n--- Dealer's Turn ---")
        self.logic.dealer_turn()
        final_dealer_hand, final_dealer_score = self.logic.get_hand_details("dealer")
        self.display_hand("dealer", final_dealer_hand, final_dealer_score)
        if self.logic.is_dealer_busted():
            print("Dealer busted!")

        # Determine and display results
        print("\n--- Game Results ---")
        results = self.logic.get_game_results()
        dealer_final_hand, dealer_final_score = self.logic.get_hand_details("dealer")
        print(f"Dealer's final hand: {dealer_final_hand} | Score: {dealer_final_score}")

        for player, hand_outcomes in results.items():
            for hand_num, outcome in hand_outcomes.items():
                player_hand, player_score = self.logic.get_hand_details(player, hand_num)
                status_text = ""
                if outcome == 1:
                    status_text = "wins"
                elif outcome == 0:
                    status_text = "loses"
                else: # 0.5
                    status_text = "ties"
                print(f"{player} (Hand {hand_num}): {player_hand} | Score: {player_score} - {status_text}!")

        print("\nGame Over!")
        self.logic.reset_game_data() # Reset for a new game

# --- To run the text-based game ---
if __name__ == "__main__":
    game = BlackjackGame()
    game.play_game()
