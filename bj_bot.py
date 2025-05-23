import random

class SimpleBlackjackAI:
    def __init__(self):
        self.hard_strategy = {
            4: ['H']*10, 8: ['H']*10, 9: ['H']*6 + ['S']*4,
            10: ['H']*3 + ['S']*7, 11: ['S']*10, 12: ['H']*3 + ['S']*7,
            13: ['S']*4 + ['H']*3 + ['S']*3, 14: ['S']*4 + ['H']*3 + ['S']*3,
            15: ['S']*4 + ['H']*3 + ['S']*3, 16: ['S']*4 + ['H']*3 + ['S']*3,
            17: ['S']*10, 18: ['S']*10, 19: ['S']*10, 20: ['S']*10
        }
        self.soft_strategy = {
            13: ['H']*10, 14: ['H']*10, 15: ['H']*6 + ['S']*4,
            16: ['H']*3 + ['S']*7, 17: ['S']*4 + ['H']*3 + ['S']*3,
            18: ['S']*10, 19: ['S']*10
        }
        self.pair_strategy = {
            4: ['P']*5 + ['H']*5, 6: ['P']*6 + ['H']*4, 8: ['H']*10,
            10: ['S']*10, 12: ['P']*4 + ['H']*6, 14: ['P']*8 + ['H']*2,
            16: ['P']*10, 18: ['P']*10, 20: ['S']*10
        }

    def decide_action(self, player_hand, dealer_upcard, can_split=True, is_split_hand=False):
        total, soft = self._calculate_total(player_hand)
        dealer_value = self._card_value(dealer_upcard)
        
        if len(player_hand) == 2 and total == 21:
            return 'stand'
            
        if can_split and not is_split_hand and len(player_hand) == 2 and player_hand[0] == player_hand[1]:
            pair_value = self._card_value(player_hand[0]) * 2
            action = self._get_pair_action(pair_value, dealer_value)
            if 'P' in action:
                return 'split'
        
        if soft:
            action = self._get_soft_action(total, dealer_value)
        else:
            action = self._get_hard_action(total, dealer_value)
        
        return action.lower()

    def _get_hard_action(self, total, dealer_value):
        for threshold in sorted(self.hard_strategy.keys(), reverse=True):
            if total >= threshold:
                dealer_idx = min(dealer_value - 2, 9)
                return self.hard_strategy[threshold][dealer_idx]
        return 'h'

    def _get_soft_action(self, total, dealer_value):
        for threshold in sorted(self.soft_strategy.keys(), reverse=True):
            if total >= threshold:
                dealer_idx = min(dealer_value - 2, 9)
                return self.soft_strategy[threshold][dealer_idx]
        return 'h'

    def _get_pair_action(self, pair_value, dealer_value):
        for threshold in sorted(self.pair_strategy.keys(), reverse=True):
            if pair_value >= threshold:
                dealer_idx = min(dealer_value - 2, 9)
                return self.pair_strategy[threshold][dealer_idx]
        return 'h'

    def _calculate_total(self, hand):
        total = 0
        aces = 0
        for card in hand:
            val = self._card_value(card)
            total += val
            if card == 'A':
                aces += 1
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        return total, (aces > 0)

    def _card_value(self, card):
        if card in ['J', 'Q', 'K']:
            return 10
        elif card == 'A':
            return 11
        else:
            return int(card)

class BjGame:
    def __init__(self):
        self.deck = self._create_deck()
        self.ai = SimpleBlackjackAI()
        self.reset_game()

    def reset_game(self):
        self.player_hands = []
        self.dealer_hand = []
        self.current_hand_idx = 0
        self.game_active = False
        self.shuffle()

    def _create_deck(self, decks=6):
        ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        return ranks * 4 * decks

    def shuffle(self):
        random.shuffle(self.deck)

    def deal_card(self):
        return self.deck.pop()

    def start_round(self):
        self.reset_round()
        self.player_hands = [[self.deal_card(), self.deal_card()]]
        self.dealer_hand = [self.deal_card(), self.deal_card()]
        self.game_active = True
        return self.player_hands[0], self.dealer_hand[0]

    def reset_round(self):
        self.player_hands = []
        self.dealer_hand = []
        self.current_hand_idx = 0
        self.game_active = False

    def play_ai_turn(self):
        while self.game_active and self.current_hand_idx < len(self.player_hands):
            hand = self.player_hands[self.current_hand_idx]
            total, _ = self._calculate_total(hand)
            
            if total > 21:
                self.current_hand_idx += 1
                continue
                
            action = self.ai.decide_action(
                hand,
                self.dealer_hand[0],
                can_split=(len(self.player_hands) < 4),
                is_split_hand=(self.current_hand_idx > 0)
            )
            
            if action == 'hit':
                hand.append(self.deal_card())
            elif action == 'stand':
                self.current_hand_idx += 1
            elif action == 'split':
                self._handle_split(hand)
            
            if self.current_hand_idx >= len(self.player_hands):
                self.game_active = False

    def _handle_split(self, hand):
        if len(self.player_hands) >= 4: return
        card = hand[0]
        self.player_hands.remove(hand)
        self.player_hands.append([card, self.deal_card()])
        self.player_hands.append([card, self.deal_card()])

    def play_dealer_turn(self):
        total, soft = self._calculate_total(self.dealer_hand)
        while total < 17 or (total == 17 and soft):
            self.dealer_hand.append(self.deal_card())
            total, soft = self._calculate_total(self.dealer_hand)
        return total

    def _calculate_total(self, hand):
        total = 0
        aces = 0
        for card in hand:
            val = self._card_value(card)
            total += val
            if card == 'A':
                aces += 1
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        return total, (aces > 0)

    def _card_value(self, card):
        if card in ['J', 'Q', 'K']:
            return 10
        elif card == 'A':
            return 11
        else:
            return int(card)

    def determine_winner(self, player_hand):
        player_total, _ = self._calculate_total(player_hand)
        dealer_total, _ = self._calculate_total(self.dealer_hand)
        if player_total > 21:
            return 'dealer'
        elif dealer_total > 21:
            return 'player'
        elif player_total > dealer_total:
            return 'player'
        elif dealer_total > player_total:
            return 'dealer'
        else:
            return 'push'

# if __name__ == "__main__":
#     game = BjGame()
#     game.start_round()
#     print("Player:", game.player_hands[0])
#     print("Dealer shows:", game.dealer_hand[0])
#     game.play_ai_turn()
#     game.play_dealer_turn()
#     print("Final Dealer:", game.dealer_hand)
#     for i, hand in enumerate(game.player_hands):
#         print(f"Hand {i+1}: {hand} -> {game.determine_winner(hand)}")







       
       
       
       
       
       
       
 # test remove later 
game = BjGame()
game.player_hands = [['7', '7']]  # Hard 17
game.dealer_hand = ['6', '?']     # Dealer shows 6
game.play_ai_turn()
print(f"Hand: {game.player_hands[0]} -> Action: Stand (expected)")
