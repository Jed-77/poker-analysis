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


class PokerTable:
    def __init__(self, table_players):
        self.num_players = len(table_players)
        if self.num_players > 8:
            sys.exit("Too Many Players")
        self.table_players = table_players
        self.num_hands = 0      # make sure to increment
        self.bet_history = [0]  # needs to be updated with small and big bland

    def get_table_position(self):
        # will change the position at the table
        position = {(position-self.num_hands) % self.num_players: players for position, players in enumerate(self.table_players)}
        return collections.OrderedDict(sorted(position.items()))

    def display_chip_count(self):
        [print(player) for player in self.table_players]

    def card_dealer(self, cards):
        """ Function to deal a pack of shuffled cards to n poker players and the flop, turn and river. """
        player_classifier = {}
        table_classifier = {}
        for position, player in self.get_table_position().items():
            player_classifier[player.name] = [cards[position], cards[position+self.num_players]]
            #player.set_hand(cards[position], cards[position+self.num_players]) could be useful
        table_classifier['Flop'] = [cards[2*self.num_players+1], cards[2*self.num_players+2], cards[2*self.num_players+3]]
        table_classifier['Turn'] = cards[2*self.num_players + 5]
        table_classifier['River'] = cards[2*self.num_players + 7]
        return player_classifier, table_classifier

    def card_allocation(self):
        """ Function to shuffle the cards and get the cards for the table. """
        deck = CardDeck()
        deck.shuffle()
        player_cards, table_cards = self.card_dealer(deck.cards)
        return player_cards, table_cards

    def table_initialisation(self):
        # Table Active (RUN ONCE PER HAND)
        table_active = True
        # Table Position (RUN ONCE PER HAND)
        table_position = list(self.get_table_position().items())
        # Card Allocation (RUN ONCE PER HAND)
        player_cards, table_cards = self.card_allocation()
        # Betting and Active Initialisation
        # (ACTIVE TABLE IS RUN ONCE PER HAND)
        # (BETTING TABLE IS RUN ONCE FOR FLOP, TURN AND RIVER - NEED TO SET THIS BACK TO 0 ON EACH FLOP/TURN/RIVER)
        betting_table = {}
        active_table = {}
        for position, player in self.get_table_position().items():
            betting_table[player] = 0
            active_table[player] = True
        # Pot Amount (RUN ONCE PER HAND)
        pot_amount = 0

        # Loop through Betting (RUN FOR FLOP/TURN/RIVER)
        position_counter = 0

        # PREFLOP - need to update it if everyone else folds and you win!
        while True:
            # get the position and the player object from the table position (in order of who to act)
            position, player = table_position[position_counter % self.num_players]
            # If the player isn't active, then skip them
            if not active_table[player]:
                position_counter += 1
                continue
            # If the player is the only active player in the game, then they win the pot
            if len([active for active in list(active_table.values()) if active is True]) == 1:
                player.balance += pot_amount  # they win the pot
                table_active = False          # the table is no longer active
                self.num_hands += 1           # we increment the number of games completed at the table
                break
            # If its the first position, then we are in small blind so pay up!
            if position_counter == 0:
                print("{} is on Small Blind of {}".format(player.name, ps.smallBlind))
                betting_table[player] = ps.smallBlind
                player.update_balance(-ps.smallBlind)
                pot_amount += ps.smallBlind
            # If its the second position, then we are in big blind so pay up!
            elif position_counter == 1:
                print("{} is on Big Blind of {}".format(player.name, ps.bigBlind))
                betting_table[player] = ps.bigBlind
                player.update_balance(-ps.bigBlind)
                pot_amount += ps.bigBlind
            # Else, we are free to bet so do wisely!
            else:
                # min amount we can bet is the difference between the maximum value and the current player bet
                min_amount = max(betting_table.values())-betting_table[player]
                action = input("{}, would you like to Fold (F), Check (Ch), Call (Cl) or Raise (R)?".format(player.name))
                # if you fold, you are no longer active and your bet amount goes to nothing
                if action == 'F':
                    print("{} has folded".format(player.name))
                    betting_table[player] = 0
                    active_table[player] = False
                # If you check, pass play over (error handling for if you can't check)
                elif action == 'Ch':
                    if betting_table[player] < min_amount:
                        print("Cannot check! You are calling instead")
                        print("{} is calling {}".format(player.name, min_amount))
                        betting_table[player] += int(min_amount)
                        player.update_balance(-int(min_amount))
                        pot_amount += int(min_amount)
                    else:
                        print("{} is checking".format(player.name))
                # If you call, take away money from your balance and add to the pot!
                elif action == 'Cl':
                    print("{} is calling {}".format(player.name, min_amount))
                    betting_table[player] += int(min_amount)
                    player.update_balance(-int(min_amount))
                    pot_amount += int(min_amount)
                # If you raise, take away money from your balance and add to the pot!
                elif action == 'R':
                    amount = input("How much would you like to Raise it by:")
                    if int(amount) < min_amount:
                        print("Must raise to at least the call amount. Calling Instead")
                        betting_table[player] += int(min_amount)
                        player.update_balance(-int(min_amount))
                        pot_amount += int(min_amount)
                    else:
                        print("{} is raising by {}".format(player.name, amount))
                        betting_table[player] += int(amount)
                        player.update_balance(-int(amount))
                        pot_amount += int(amount)
            # Print the current betting information and how many chips people have left
            print(betting_table)
            print("{} has {} left".format(player.name, player.balance))

            # cond1 important one - if all the non zero bets (so excl. folds) are the same, then we can move on
            cond1 = (len(set({bet for player, bet in betting_table.items() if bet != 0})) == 1)
            # cond2 it must go past the number of players
            # this is only valid for pre flop (although remember that even if people do fold, we still
            # ... iterate over them but we just continue quickly)
            cond2 = (position_counter > self.num_players)

            if cond1 & cond2:
                # if only one active player exists at this point in the code, it must be the next player
                # ... as it can't be this player as they didn't get caught in the if statement earlier
                # so we continue to make sure they get the pot paid to them
                if len([active for active in list(active_table.values()) if active is True]) == 1:
                    continue
                else:
                    break
            # Be sure to move the position to next player
            position_counter += 1


        # END OF THE PREFLOP - WE HAVE THE BET AMOUNT, THE ACTIVE TABLE AND THE POT AMOUNT
        # if the game is active then the pot can still be won!
        # if not then we already move onto the next game
        print("\nIs the table active?: {}".format(table_active))
        print("\nPot size is {}".format(pot_amount))
        print("\nAmount bet per active player is:")
        print(betting_table)
        print("\nActive player is:")
        print(active_table)

        # print peoples stack
        for player, bet in betting_table.items():
            print(player.name)
            print(player.balance)

        # FLOP
        print(table_cards['Flop'])
        # start the loop again and take another round of betting
        # also look up if the table is still active, if not the round is done
        # do a further qa that the sum of all chips is the same as begining
        # this is why we could do with a function to do it




# Main
player_list = [PokerPlayer("Jed"), PokerPlayer("Tom"), PokerPlayer("Josh"), PokerPlayer("Will")]
table = PokerTable(player_list)
print(table.get_table_position())
table.table_initialisation()


