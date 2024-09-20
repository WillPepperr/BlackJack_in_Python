import random


class Card:
    suits = ['h', 'd', 'c', 's']
    values = {
        '2': 2, '3': 3, '4': 4, '5': 5,
        '6': 6,
        '7': 7, '8': 8, '9': 9,
        '10': 10, 'J': 10, 'Q': 10, 'K': 10,
        'A': 11
    }

    def __init__(self, suit, value):
        self.suit = suit
        self.face = value
        self.value = Card.values[value]

    def __repr__(self):
        return f"{self.face}{self.suit}({self.value})"


class Shoe:
    def __init__(self, num_decks, burn_percentage):
        self.all_cards = num_decks * 52
        self.decks = num_decks
        self.burned_cards = []
        self.shoe_cards = []
        self.dealer_hidden_card = []
        self.burn_percentage = burn_percentage
        self.create_shoe()
        self.running_count = 0
        self.true_count = 0

    def create_shoe(self):
        self.shoe_cards = [Card(s, v) for _ in range(self.decks) for s in Card.suits for v in Card.values]
        self.shuffle_shoe()

    def shuffle_shoe(self):
        random.shuffle(self.shoe_cards)

    def deal(self):
        card = self.shoe_cards.pop()
        self.burned_cards.append(card)
        return card

    def percentage_burned(self):
        return len(self.burned_cards) / self.all_cards

    def update_running_count(self):
        running = self.running_count
        for card in self.burned_cards:
            if card.value < 7:
                running += 1
            if card.value > 9:
                running -= 1
        return running

    def update_true_count(self):
        rounded_cards = max(round((len(self.shoe_cards) / 52)), 1)
        true_count= round(self.update_running_count() / rounded_cards)
        return true_count


    def remove_hidden_count(self):
        hidden_card = self.burned_cards.pop()
        self.dealer_hidden_card.append(hidden_card)

    def count_hidden_card(self):
        hidden_card = self.dealer_hidden_card.pop()
        self.burned_cards.append(hidden_card)

class Hand:
    def __init__(self, is_player_hand=True, hand_number=0):
        self.cards = []
        self.is_player_hand = is_player_hand
        self.can_split = False
        self.hand_number = hand_number
        self.num_aces = sum(1 for card in self.cards if card.face == 'A')
        self.has_doubled = False
        self.has_split = False

    def add_card(self, card):
        self.cards.append(card)

    def hand_value(self):
        value = sum(card.value for card in self.cards)
        self.num_aces = sum(1 for card in self.cards if card.face == 'A')
        ace_with_value_eleven = self.num_aces
        while value > 21 and ace_with_value_eleven > 0:
            value -= 10
            ace_with_value_eleven -= 1
        return value

    def soft_seventeen(self):
        value = self.hand_value()
        if value == 17 and self.num_aces > 0:
            soft_seventeen_check = sum(card.value for card in self.cards if card.face != 'A')
            if soft_seventeen_check < 7:
                return True
        return False

    def update_split_ability(self):
        if len(self.cards) == 2 and self.cards[0].value == self.cards[1].value:
            self.can_split = True
        else:
            self.can_split = False

    def can_double(self):
        return len(self.cards) == 2

    def hand_split(self):
        if not self.can_split:
            raise ValueError("Cannot split this hand")
        self.hand_number += 1
        if self.hand_number == 1:
            self.hand_number += 1
        next_hand = Hand(is_player_hand=self.is_player_hand, hand_number=self.hand_number)
        next_hand.add_card(self.cards.pop())
        self.has_split = True
        return next_hand

    def double_down(self):
        if not self.can_double():
            raise ValueError("Cannot double")
        self.has_doubled = True

    def __repr__(self):
        hand_label = f"Hand {self.hand_number}" if self.hand_number != 0 else "Hand"
        return f"{hand_label}: {self.cards} {self.hand_value()}"


class Player:
    def __init__(self, initial_balance=1000):
        self.balance = initial_balance

    def place_bet(self, bet_amount):
        bet_amount = int(bet_amount)
        if bet_amount > self.balance:
            raise ValueError("Insufficient funds for this bet")
        self.balance -= bet_amount
        return bet_amount

    def win_bet(self, bet_amount, win_multiplier):
        self.balance += bet_amount * win_multiplier


class BlackjackGame:
    def __init__(self, num_decks, game_burn_percentage):
        self.shoe = Shoe(num_decks, game_burn_percentage)
        self.player = Player()
        self.player_hands = []
        self.dealer_hand = None
        self.bet_amount = 0
        self.game_loop()

    def deal_initial_cards(self):
        self.player_hands = [Hand(is_player_hand=True)]
        self.dealer_hand = Hand(is_player_hand=False)
        for hand in self.player_hands:
            hand.add_card(self.shoe.deal())
            hand.add_card(self.shoe.deal())
        self.dealer_hand.add_card(self.shoe.deal())
        self.dealer_hand.add_card(self.shoe.deal())
        print(f"\nDealer's card: {self.dealer_hand.cards[0]}")
        print(f"Dealer's card: [Hidden]")
        if self.check_blackjack(self.dealer_hand):
            self.dealer_blackjack()
        else:
            all_player_blackjacks = [self.check_blackjack(hand) for hand in self.player_hands]
            if any(all_player_blackjacks):
                self.player_blackjack()

    def check_blackjack(self, hand):
        """Check if the given hand is a Blackjack."""
        return hand.hand_value() == 21 and (len(hand.cards) == 2 and hand.has_split is False)

    def dealer_blackjack(self):
        print(f"Dealer {self.dealer_hand}")
        print(f"Player {self.player_hands}")
        print("Dealer has Blackjack!")
        for hand in self.player_hands:
            if self.check_blackjack(hand):
                print("Push: Player also has Blackjack")
                self.player.win_bet(self.bet_amount, 1)  # Return the bet amount
            else:
                print(f"Player loses -{self.bet_amount}")

    def player_blackjack(self):
        print(f"{self.player_hands}")
        print(f"Dealer {self.dealer_hand}")
        print("Player has Blackjack!")
        for hand in self.player_hands:
            if self.check_blackjack(hand):
                self.player.win_bet(self.bet_amount, 2.5)  # 1.5x winnings for Blackjack

    def player_turn(self):
        for i, hand in enumerate(self.player_hands):
            if not self.check_blackjack(hand):  # Skip player turn if they have Blackjack
                print(f"Running Count:{self.shoe.update_running_count()}        True Count:{self.shoe.update_true_count()}")
                while True:
                    hand.update_split_ability()
                    action = input(f"{hand} (hit/stand/double/split): ").strip().lower()
                    if action == 'hit':
                        hand.add_card(self.shoe.deal())
                        hand.hand_value()
                        print(hand)
                        if hand.hand_value() > 21:
                            print("Hand busts!")
                            break
                    elif action == 'stand':
                        break
                    elif action == 'double':
                        if hand.can_double():
                            hand.double_down()
                            hand.has_doubled = True
                            hand.add_card(self.shoe.deal())
                            Player.place_bet(self.player, self.bet_amount)
                            print(hand)
                            hand.hand_value()
                            if hand.hand_value() > 21:
                                print("Hand busts!")
                            break
                        else:
                            print("Cannot double down")
                    elif action == 'split':
                        if hand.can_split:
                            new_hand = hand.hand_split()
                            new_hand.add_card(self.shoe.deal())
                            hand.add_card(self.shoe.deal())
                            self.player_hands.append(new_hand)
                            Player.place_bet(self.player, self.bet_amount)
                            hand.has_split = True
                            print(f"New hands: {hand} and {new_hand}")
                        else:
                            print("Cannot split")
                    else:
                        print("Invalid action")

    def dealer_turn(self):
        print(f"\nDealer's card: {self.dealer_hand.cards[0]}")
        print(f"Dealer's  card: {self.dealer_hand.cards[1]}")
        if self.dealer_hand.hand_value() == 17 and self.dealer_hand.soft_seventeen():
            self.dealer_hand.add_card(self.shoe.deal())
            print(self.dealer_hand)
            self.dealer_hand.hand_value()
        while self.dealer_hand.hand_value() < 17:
            self.dealer_hand.add_card(self.shoe.deal())
            print(self.dealer_hand)
            if self.dealer_hand.hand_value() > 21:
                print("Dealer busts!")
                break
        print(f"Dealer's final {self.dealer_hand}")

    def determine_winner(self):
        dealer_value = self.dealer_hand.hand_value()
        results = []
        for i, hand in enumerate(self.player_hands):
            player_value = hand.hand_value()
            if player_value > 21:
                if hand.has_doubled is True:
                    result = f"Hand {i + 1} busted -${self.bet_amount * 2}"
                else:
                    result = f"Hand {i + 1} busted -${self.bet_amount}"
            elif dealer_value > 21 or player_value > dealer_value:
                if hand.has_doubled is True:
                    result = f"Hand {i + 1} wins +${self.bet_amount * 2}"
                else:
                    result = f"Hand {i + 1} wins +${self.bet_amount}"
                self.player.win_bet(self.bet_amount, 2)  # Double the bet amount if the player wins
                if hand.has_doubled is True:
                    self.player.win_bet(self.bet_amount, 2)
            elif player_value < dealer_value:
                if hand.has_doubled is True:
                    result = f"Hand {i + 1} loses -${self.bet_amount * 2}"
                else:
                    result = f"Hand {i + 1} loses -${self.bet_amount}"
            else:
                result = f"Hand {i + 1} is a push"
                self.player.win_bet(self.bet_amount, 1)  # Return the bet amount if it's a tie
                if hand.has_doubled is True:
                    self.player.win_bet(self.bet_amount, 1)
            results.append(result)
        return results

    def game_loop(self):
        while True:
            print(f"\nCurrent balance: ${self.player.balance} \nRunning Count:{self.shoe.update_running_count()}    True Count:{self.shoe.update_true_count()}")
            while True:
                try:
                    self.bet_amount = int(input("Place your bet: "))
                    break
                except:
                    print("Enter a number")
            try:
                self.player.place_bet(self.bet_amount)
                self.deal_initial_cards()
                if not self.check_blackjack(self.dealer_hand) and all(not self.check_blackjack(hand) for hand in self.player_hands):
                    self.shoe.remove_hidden_count()  # for card counting
                    self.player_turn()
                    if any(hand.hand_value() <= 21 for hand in self.player_hands):  # Dealer only has a turn if player has not busted all hands
                        self.dealer_turn()
                    results = self.determine_winner()
                    for result in results:
                        print(result)
                    self.shoe.count_hidden_card()  # Add hidden card to burned cards
                    if self.shoe.percentage_burned() > self.shoe.burn_percentage:
                        self.shoe.shoe_cards.clear()
                        self.shoe.burned_cards.clear()
                        self.shoe.create_shoe()
                        print("Deck shuffled!")
            except ValueError as e:
                print(e)


if __name__ == "__main__":
    game = BlackjackGame(num_decks=8, game_burn_percentage=.80)
