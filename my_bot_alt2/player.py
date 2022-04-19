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
import pickle

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
        self.hand_strength = {}
        self.opp_bluffs = 0
        self.opp_bluff_pct = 0
        self.opp_bet_first = 0
        self.opp_bets = 10

        with open("handstrengths.pickle", 'rb') as handle:
            self.pf_hand_strengths = pickle.load(handle)

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
        # self.cards_suited = (my_cards[0][1] == my_cards[1][1])

        # if my_cards[0][0] == my_cards[1][0]:
        #     self.rank_strength = 3
        # elif (my_cards[0][0] in "AKQ") and (my_cards[1][0] in "AKQ"):
        #     self.rank_strength = 2
        # elif (my_cards[0][0] in "AKQJT") or (my_cards[1][0] in "AKQJT"):
        #     self.rank_strength = 1
        # else:
        #     self.rank_strength = 0
        # print(self.cards_suited, self.rank_strength)

        self.opp_bluff_pct = self.opp_bluffs / self.opp_bets


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
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        self.preflop_raiser = False
        self.hand_strength = {}
        if (my_delta > 0 and opp_cards != []):
            self.opp_bluffs += self.opp_bet_first
        if opp_cards == []:
            self.opp_bluffs += self.opp_bet_first/(street+2)
        else:
            self.opp_bluffs -= self.opp_bet_first
        self.opp_bets += self.opp_bet_first
        self.opp_bet_first = 0

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
        potsize = my_contribution + opp_contribution

        potodds = continue_cost / (potsize + continue_cost)
        foldfreq = (continue_cost) / (potsize + continue_cost)
        
        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        # print(my_cards)
        try:
            hand_strength = self.hand_strength[street]
        except KeyError:
            if street == 0:
                try:
                    self.hand_strength[street] = self.pf_hand_strengths[(my_cards[0], my_cards[1])]
                except KeyError:
                    self.hand_strength[street] = self.pf_hand_strengths[(my_cards[1], my_cards[0])]
            else:
                self.hand_strength[street] = calc_equity(my_cards, None, board_cards, phase=street)
                print("recalculating...")
            hand_strength = self.hand_strength[street]
        print(my_cards, hand_strength)

        if street >= 3 and (CallAction in legal_actions or RaiseAction in legal_actions):
            # Evaluate hand better if opp bluffs a lot, and worse if opp bets big
            print(opp_pip, opp_stack)
            print("Bluff pct:", self.opp_bluff_pct, "stackpct=", (opp_pip/(opp_pip+opp_stack)))
            hand_strength = hand_strength + 1*self.opp_bluff_pct - 0.8*(opp_pip/(opp_pip+opp_stack))
            print("Adjusted hand strength:", hand_strength)
        my_action = FoldAction()

        if CallAction in legal_actions and street != 0:
            self.opp_bet_first += 1

        # Pre-flop play
        if street == 0:
            if RaiseAction in legal_actions and hand_strength > 0.2 and continue_cost <= 1: # Open raise
                my_action = RaiseAction(min(max_raise, max(6, min_raise)))
                self.preflop_raiser = True
            elif RaiseAction in legal_actions and ((continue_cost > 1 and hand_strength >= 0.7) or random.random() <= 0.05): # Three-bet
                my_action = RaiseAction(min(max_raise, max(3*continue_cost, min_raise)))
                self.preflop_raiser = True
            elif CallAction in legal_actions and self.preflop_raiser == False and hand_strength > 0.3: # Call an open raise
                my_action = CallAction()
            elif CallAction in legal_actions and self.preflop_raiser == True and hand_strength > 0.6: # Call a three-bet
                my_action = CallAction()
            elif CheckAction in legal_actions:
                my_action = CheckAction()
        
        # Flop play
        elif street == 3:
            # C-bet
            if self.preflop_raiser:
                # OOP or checks to us
                if RaiseAction in legal_actions and CallAction not in legal_actions:
                    print("c-betting")
                    my_action = RaiseAction(min(potsize//4, max_raise))
                # Villain bets
                elif CallAction in legal_actions:
                    if hand_strength >= potodds or (random.random() < 0.1 and hand_strength > 0.15):
                        my_action = CallAction()
                elif CheckAction in legal_actions:
                    my_action = CheckAction()
            
            # Opponent raised or we checked pre-flop
            else:
                # Check is default action
                if CheckAction in legal_actions:
                    my_action = CheckAction()
                # Bluff raise
                if random.random() <= 0.05:
                    if RaiseAction in legal_actions and potsize//4 >= min_raise:
                        my_action = RaiseAction(max(min_raise, min(potsize//4, max_raise, my_stack)))
                else:
                    # Reraise a bet
                    if hand_strength >= 0.8:
                        if RaiseAction in legal_actions:
                            my_action = RaiseAction(max(min_raise, min(2*continue_cost, max_raise, my_stack)))
                    # If villain bets at us, call only if we have the odds
                    elif CallAction in legal_actions and hand_strength >= potodds:
                        my_action = CallAction()
                    # If villain checks or it is our turn to act, bet
                    elif RaiseAction in legal_actions and CallAction not in legal_actions and hand_strength >= 0.2:
                        my_action = RaiseAction(max(min_raise, min(potsize//4, max_raise, my_stack)))
                    
        # Turn play
        elif street == 4:
            # Check is default action
            if CheckAction in legal_actions:
                my_action = CheckAction()
            # Bluff raise
            if random.random() <= 0.1 and RaiseAction in legal_actions:
                my_action = RaiseAction(max(min_raise, min(2*potsize//3, max_raise, my_stack)))
            else:
                # Reraise a bet
                if hand_strength >= 0.85:
                    if RaiseAction in legal_actions:
                        my_action = RaiseAction(max(min_raise, min(2*continue_cost, max_raise, my_stack)))
                # If villain bets at us, call only if we have the odds
                elif CallAction in legal_actions and hand_strength >= potodds:
                    my_action = CallAction()
                # If villain checks or it is our turn to act, bet
                elif RaiseAction in legal_actions and CallAction not in legal_actions and hand_strength >= 0.4:
                    my_action = RaiseAction(max(min_raise, min(2*potsize//3, max_raise, my_stack)))
                # Don't fold too often to avoid bluffing exploitations
                elif random.random() > (foldfreq + 0.2) and CallAction in legal_actions:
                    my_action = CallAction() 
                
        # River play
        else:
            if RaiseAction in legal_actions:
                raiseamount = min(max(min_raise, random.randint(2*potsize//3, int(2.5*potsize))), max_raise)
            # raiseamount = min_raise+1

            # Default check if possible
            if CheckAction in legal_actions:
                        my_action = CheckAction()
            if random.random() > 0.95:
                # Bet if we have it
                if RaiseAction in legal_actions and hand_strength >= 0.7:
                    my_action = RaiseAction(raiseamount)
                    # if raiseamount <= my_stack:
                    # else:
                    #     my_action = CallAction()
                # Call if we have the odds
                elif CallAction in legal_actions and hand_strength >= potodds:
                    my_action = CallAction()
            # Bluff sometimes
            else:
                if RaiseAction in legal_actions:
                    my_action = RaiseAction(raiseamount)
        #     print(my_action, min_raise, max_raise, min_cost, max_cost, my_stack, opp_stack)
        # print(legal_actions, my_action)
        return my_action


if __name__ == '__main__':
    run_bot(Player(), parse_args())
