'''
Simple example pokerbot, written in Python.
'''
from helpers import *
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import random

class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''

        # Implement a (very) rudimentary card strength scheme
        self.cards_suited = False
        self.rank_strength = 0
        self.preflop_raiser = False

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        print(my_cards)
        self.cards_suited = (my_cards[0][1] == my_cards[1][1])

        if my_cards[0][0] == my_cards[1][0]:
            self.rank_strength = 3
        elif (my_cards[0][0] in "AKQ") and (my_cards[1][0] in "AKQ"):
            self.rank_strength = 2
        elif (my_cards[0][0] in "AKQJT") or (my_cards[1][0] in "AKQJT"):
            self.rank_strength = 1
        else:
            self.rank_strength = 0
        print(self.cards_suited, self.rank_strength)


    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        #previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        self.preflop_raiser = False
        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        potsize = my_contribution + opp_contribution # TODO: verify
        
        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        hand_strength = hand_rank(my_cards, board_cards)
        my_action = FoldAction()
        # Pre-flop play
        if street == 0:
            if RaiseAction in legal_actions and self.rank_strength==3 and my_cards[0][0] in "AKQ" and random.random() >= 0.1:
                my_action = RaiseAction(max_raise)
            elif RaiseAction in legal_actions and (((self.cards_suited or self.rank_strength != 0) and self.preflop_raiser == False) or (self.rank_strength==3 and my_cards[0][0] in "AKQJT9") or (self.rank_strength == 2)):
                my_action = RaiseAction(min(max_raise, max(6*continue_cost, min_raise)))
                self.preflop_raiser = True
            elif CallAction in legal_actions and self.preflop_raiser == True and (self.rank_strength >= 1):
                my_action = CallAction()
            elif CheckAction in legal_actions:
                my_action = CheckAction()
        
        # Flop play
        elif street == 3:
            # C-bet
            if self.preflop_raiser:
                # OOP or checks to us
                if RaiseAction in legal_actions and CallAction not in legal_actions:
                    my_action = RaiseAction(min(potsize//4, max_raise))
                # Villain bets
                elif CallAction in legal_actions:
                    if hand_strength <= 8 or (random.random() < 0.1 and self.rank_strength >= 1):
                        my_action = CallAction()
                elif CheckAction in legal_actions:
                    my_action = CheckAction()
            
            # Opponent raised or we checked
            else:
                if random.random() <= 0.29:
                    if RaiseAction in legal_actions and CallAction not in legal_actions:
                        my_action = RaiseAction(min(2*potsize//3, max_raise))
                    elif CallAction in legal_actions and (hand_strength <= 8 or self.rank_strength >= 2):
                        my_action = CallAction()
                    elif CheckAction in legal_actions:
                        my_action = CheckAction()
                else:
                    if hand_strength <= 8:
                        if RaiseAction in legal_actions:
                            my_action = RaiseAction(min(max(2*potsize//3, min_raise), max_raise))
                        elif CallAction in legal_actions:
                            my_action = CallAction()
                    elif CheckAction in legal_actions:
                        my_action = CheckAction()
        # Turn play
        elif street == 4:
            if random.random() <= 0.50 and RaiseAction in legal_actions:
                my_action = RaiseAction(min(2*potsize//3, max_raise))
            else:
                if hand_strength <= 5:
                    if RaiseAction in legal_actions:
                        my_action = RaiseAction(max_raise)
                    elif CallAction in legal_actions:
                        my_action = CallAction()
                elif hand_strength <= 7:
                    if RaiseAction in legal_actions:
                        my_action = RaiseAction(min(2*potsize, max_raise))
                    elif CallAction in legal_actions:
                        my_action = CallAction()
                elif hand_strength == 8:
                    if RaiseAction in legal_actions:
                        my_action = RaiseAction(min(2*potsize//3, max_raise))
                    elif CallAction in legal_actions and continue_cost <= potsize/2:
                        my_action = CallAction()
                else:
                    fold_freq = (continue_cost) / (potsize + continue_cost)
                    if random.random() > fold_freq and CallAction in legal_actions:
                        my_action = CallAction()                
                    elif CheckAction in legal_actions:
                        my_action = CheckAction()
        else:
            if random.random() <= 0.75 and RaiseAction in legal_actions:
                my_action = RaiseAction(min(2*potsize//3, max_raise))
            else:
                if hand_strength <= 5:
                    if RaiseAction in legal_actions:
                        my_action = RaiseAction(max_raise)
                    elif CallAction in legal_actions:
                        my_action = CallAction()
                elif hand_strength <= 7:
                    if RaiseAction in legal_actions:
                        my_action = RaiseAction(min(2*potsize, max_raise))
                    elif CallAction in legal_actions:
                        my_action = CallAction()
                else:
                    fold_freq = (continue_cost) / (potsize + continue_cost)
                    if random.random() > fold_freq and CallAction in legal_actions:
                        my_action = CallAction()                
                    elif CheckAction in legal_actions:
                        my_action = CheckAction()
        return my_action


if __name__ == '__main__':
    run_bot(Player(), parse_args())