__author__ = "Jed Scanlon"

import sys
import random
import collections
import poker_settings as ps


class Card:
    def __init__(self, card_name):
        self.card_name = card_name
        self.value, self.suit = card_name.split('_')
        self.value_numeric = ps.cardValue[self.value]


class CardDeck:
    def __init__(self):
        self.cards = ps.validDeck

    def __str__(self):
        return str(self.cards)

    def shuffle(self):
        self.cards = random.sample(self.cards, len(self.cards))


class PokerPlayer:
    def __init__(self, name):
        self.name = name
        self.balance = ps.startingChipCount
        self.active = True
        self.card1 = None
        self.card2 = None

    def __str__(self):
        return "{}".format(self.name)

    def reset_player(self):
        print('Resetting for player: {}'.format(self.name))
        self.active = True
        self.card1 = None
        self.card2 = None

    def set_hand(self, card1, card2):
        self.card1 = card1
        self.card2 = card2

    def update_balance(self, amount):
        self.balance += amount

    #def hand_evaluation(self, table_cards=None):
        # f(card1, card2, other group (which is flop, turn or river as we evaluate on each)
    #    print('{} is evaluating...'.format(self.name))

    def player_action(self, action_type, min_amount=0, amount=0):
        if action_type == 'Fold':
            print('{} folds.'.format(self.name))
            self.active = False
            return 0
        elif action_type == 'Check':
            if min_amount > 0:
                print('You cannot check as minimum bet is {}'.format(min_amount))
                return self.player_action('Call', min_amount=min_amount)
            print('{} checks.'.format(self.name))
            return 0
        elif action_type == 'Call':
            self.balance -= min_amount
            print('{} calls {}.'.format(self.name, min_amount))
            return min_amount
        elif action_type == 'Raise':
            if amount < min_amount:
                print('You cannot bet less than minimum bet of {}'.format(min_amount))
                self.player_action('Call', min_amount=min_amount)
                return min_amount
            else:
                print('{} raises to {}.'.format(self.name, amount))
                self.balance -= amount
                return amount
        else:
            sys.exit("Not Valid Action")


class PokerTable:
    def __init__(self, table_players):
        self.num_players = len(table_players)
        if self.num_players > 8:
            sys.exit("Too Many Players")
        self.table_players = table_players
        self.num_hands = 0  # make sure to increment
        self.bet_history = [0]  # needs to be updated with small and big bland

    #def __str__(self):
    #    return str({position: players.name for position, players in enumerate(self.table_players)})

    def get_table_position(self):
        # will change the position at the table
        position = {(position-self.num_hands) % self.num_players: players for position, players in enumerate(self.table_players)}
        return collections.OrderedDict(sorted(position.items()))

    def display_chip_count(self):
        [print(player) for player in self.table_players]

    def card_allocation(self, cards):
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

    def run_pre_flop(self):
        deck = CardDeck()
        deck.shuffle()
        player_cards, table_cards = self.card_allocation(deck.cards)
        print(player_cards)
        print(table_cards)
        # Betting Initialisation
        betting_table = {}
        for position, player in self.get_table_position().items():
            betting_table[player] = 0
        active_table = {}
        for position, player in self.get_table_position().items():
            active_table[player] = True

        # Loop through Betting
        position_counter = 0
        table_position = list(self.get_table_position().items())
        print(table_position)

        # WORKING GOOD - NEED TO UPDATE THE F FUNCTIONALITY (ACTIVE = FALSE)
        while position_counter < 10:
            position, player = table_position[position_counter % self.num_players]
            if position_counter == 0:
                print("{} is on Small Blind of {}".format(player.name, ps.smallBlind))
                betting_table[player] = ps.smallBlind
                player.update_balance(-ps.smallBlind)
            elif position_counter == 1:
                print("{} is on Big Blind of {}".format(player.name, ps.bigBlind))
                betting_table[player] = ps.bigBlind
                player.update_balance(-ps.bigBlind)
            else:
                min_amount = max(betting_table.values())-betting_table[player]
                action = input("{}, would you like to Fold (F), Check (Ch), Call (Cl) or Raise (R)?".format(player.name))
                if action == 'F':
                    print("{} has folded".format(player.name))
                    active_table[player] = False
                elif action == 'Ch':
                    if betting_table[player] < min_amount:
                        print("Cannot check! You are calling instead")
                        print("{} is calling {}".format(player.name, min_amount))
                        betting_table[player] += int(min_amount)
                        player.update_balance(-int(min_amount))
                    else:
                        print("{} is checking".format(player.name))
                elif action == 'Cl':
                    print("{} is calling {}".format(player.name, min_amount))
                    betting_table[player] += int(min_amount)
                    player.update_balance(-int(min_amount))
                elif action == 'R':
                    amount = input("How much would you like to Raise it by:")
                    if int(amount) < min_amount:
                        print("Must raise to at least the call amount. Calling Instead")
                        betting_table[player] += int(min_amount)
                        player.update_balance(-int(min_amount))
                    else:
                        print("{} is raising to {}".format(player.name, amount))
                        betting_table[player] += int(amount)
                        player.update_balance(-int(amount))
            print(betting_table)
            print("{} has {} left".format(player.name, player.balance))
            if (position_counter % self.num_players == 1) & (len(set(betting_table.values())) == 1):
                # if on big blind and everyone has bet the same, we are done
                break
            position_counter += 1

        print(betting_table)
        print(active_table)



    #def run_hand(self):
    #    pot_amount = 0
    #    # Reset each player (so they have no cards and are active in the round)
    #    [player.reset_player() for player in self.table_players]
    #    # Deal the cards and initialise the card allocation
    #    deck = CardDeck()
    #    deck.shuffle()
    #    player_hands, table_hands = self.deck_classifier(deck.cards)
    #
    #    # Pre Flop
    #    print("\n Each player was dealt...")
    #    print(player_hands)
    #    # Each player will evaluate their hand pre flop (so no parameter)
    #    #[player.hand_evaluation() for player in player_list]
    #    # Each player bets
    #    for player in self.table_players:
    #        action = input("What should {} do?".format(player))
    #        amount = input("How much?")
    #        player.player_action(action, max(self.bet_history), int(amount))#
    #
    #    print("\nPre Flop Pot Amount is: {}".format(pot_amount))

        # Flop
     #   print("Flop: {}".format(table_hands['Flop']))
        #[player.hand_evaluation(FLOP) for player in player_list]

        # Turn
    #    print("Turn: {}{}".format(table_hands['Flop'], [table_hands['Turn']]))
        # [player.hand_evaluation(FLOP) for player in player_list]

        # River
    #    print("River: {}{}{}".format(table_hands['Flop'], [table_hands['Turn']], [table_hands['River']]))
        # [player.hand_evaluation(FLOP) for player in player_list]
        # make sure to increment num_hands_played




player_list = [PokerPlayer("Jed"), PokerPlayer("Tom"), PokerPlayer("Josh"), PokerPlayer("Will")]
table = PokerTable(player_list)
print(table.get_table_position())
table.run_pre_flop()


