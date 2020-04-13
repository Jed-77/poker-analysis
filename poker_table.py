__author__ = "Jed Scanlon"

import sys
import random
import poker_settings as ps


class CardDeck:
    def __init__(self):
        self.cards = ps.validDeck

    def __str__(self):
        return str(self.cards)

    def shuffle(self):
        self.cards = random.sample(self.cards, len(self.cards))


class Card:
    def __init__(self, card_name):
        self.card_name = card_name
        self.value, self.suit = card_name.split('_')
        self.value_numeric = ps.cardValue[self.value]


class PokerPlayer:
    def __init__(self, name):
        self.name = name
        self.balance = ps.startingChipCount
        self.active = True
        self.card1 = None
        self.card2 = None

    def __str__(self):
        return "{} has {} chips remaining".format(self.name, self.balance)

    def reset_player(self):
        print('Resetting for player: {}'.format(self.name))
        self.active = True
        self.card1 = None
        self.card2 = None

    def set_hand(self, card1, card2):
        self.card1 = card1
        self.card2 = card2

    #def hand_evaluation(self, table_cards=None):
        # f(card1, card2, other group (which is flop, turn or river as we evaluate on each)
    #    print('{} is evaluating...'.format(self.name))

    def player_action(self, action_type, min_amount=0, amount=0):
        if action_type == 'Fold':
            print('{} folds.'.format(self.name))
            self.active = False
        elif action_type == 'Check':
            if min_amount > 0:
                print('You cannot check as minimum bet is {}'.format(min_amount))
                self.player_action('Call', min_amount=min_amount)
            print('{} checks.'.format(self.name))
        elif action_type == 'Call':
            self.balance -= min_amount
            print('{} calls {}.'.format(self.name, min_amount))
        elif action_type == 'Raise':
            if amount < min_amount:
                print('You cannot bet less than minimum bet of {}'.format(min_amount))
                self.player_action('Call', min_amount=min_amount)
            else:
                print('{} raises to {}.'.format(self.name, amount))
                self.balance -= amount
        else:
            sys.exit("Not Valid Action")


class PokerTable:
    def __init__(self, table_players):
        self.num_players = len(table_players)
        if self.num_players > 8:
            sys.exit("Too Many Players")
        self.table_players = table_players
        self.num_hands = 0
        self.bet_history = [0]  # needs to be updated with small and big bland

    def __str__(self):
        return str({position: players.name for position, players in enumerate(self.table_players)})

    def get_table_position(self):
        # num_hands here doesnt work, we need to use the dealer chip!
        return {position: players for position, players in enumerate(self.table_players)}

    def display_chip_count(self):
        [print(player) for player in self.table_players]

    def deck_classifier(self, cards):
        player_classifier = {}
        table_classifier = {}
        for position, player in self.get_table_position().items():
            player_classifier[player.name] = [cards[position], cards[position+self.num_players]]
            player.set_hand(cards[position], cards[position+self.num_players])
        table_classifier['Flop'] = [cards[2*self.num_players+1], cards[2*self.num_players+2], cards[2*self.num_players+3]]
        table_classifier['Turn'] = cards[2*self.num_players + 5]
        table_classifier['River'] = cards[2*self.num_players + 7]
        return player_classifier, table_classifier

    def table_action(self, min_amount):
        return 0

    def run_hand(self):
        pot_amount = 0
        # Reset each player (so they have no cards and are active in the round)
        [player.reset_player() for player in player_list]
        # Deal the cards and initialise the card allocation
        deck = CardDeck()
        deck.shuffle()
        player_hands, table_hands = self.deck_classifier(deck.cards)

        # Pre Flop
        print("\n Each player was dealt...")
        print(player_hands)
        # Each player will evaluate their hand pre flop (so no parameter)
        #[player.hand_evaluation() for player in player_list]
        # Each player bets
        for player in player_list:
            action = input("What should {} do?".format(player))
            amount = input("How much?")
            player.player_action(action, max(self.bet_history), int(amount))

        print("\nPre Flop Pot Amount is: {}".format(pot_amount))

        # Flop
        print("Flop: {}".format(table_hands['Flop']))
        #[player.hand_evaluation(FLOP) for player in player_list]

        # Turn
        print("Turn: {}{}".format(table_hands['Flop'], [table_hands['Turn']]))
        # [player.hand_evaluation(FLOP) for player in player_list]

        # River
        print("River: {}{}{}".format(table_hands['Flop'], [table_hands['Turn']], [table_hands['River']]))
        # [player.hand_evaluation(FLOP) for player in player_list]





player_list = [PokerPlayer("Jed"), PokerPlayer("Tom"), PokerPlayer("Josh"), PokerPlayer("Will")]
table = PokerTable(player_list)
table.run_hand()



