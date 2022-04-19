import eval7
import random

def calc_equity(hole, opp=None, board=[], ITERS=500, phase=0):
    deck = eval7.Deck()
    hole_cards = [eval7.Card(card) for card in hole]
    # print(hole_cards)
    opp_cards = []
    if opp is not None:
        opp_cards = [eval7.Card(card) for card in opp]
    board_cards = [eval7.Card(card) for card in board]

    for card in hole_cards:
        deck.cards.remove(card)
    
    for card in opp_cards:
        deck.cards.remove(card)
    
    for card in board_cards:
        deck.cards.remove(card)
    
    score = 0
    for _ in range(ITERS):
        deck.shuffle()

        if opp is None:
            opp_cards = deck.peek(2)
        
        comm = board_cards + deck.peek(7-len(board_cards))[2:]

        my_hand = hole_cards + comm
        opp_hand = opp_cards + comm
        # Take into account swapping
        if phase == 0:
            for i in range(2):
                if random.random() <= 0.145:
                    my_hand[i] = deck.peek(9)[7+i]
            for i in range(2):
                if random.random() <= 0.145:
                    opp_hand[i] = deck.peek(11)[9+i]
        if phase == 3:
            for i in range(2):
                if random.random() <= 0.1:
                    my_hand[i] = deck.peek(9)[7+i]
            for i in range(2):
                if random.random() <= 0.1:
                    opp_hand[i] = deck.peek(11)[9+i]
        elif phase == 4:
            for i in range(2):
                if random.random() <= 0.05:
                    my_hand[i] = deck.peek(9)[7+i]
            for i in range(2):
                if random.random() <= 0.05:
                    opp_hand[i] = deck.peek(11)[9+i]

        my_hand_value = eval7.evaluate(my_hand)
        opp_hand_value = eval7.evaluate(opp_hand)
        # print(my_hand, opp_hand)

        if my_hand_value > opp_hand_value:
            score += 2
        elif my_hand_value == opp_hand_value:
            score += 1
        else:
            score += 0
    
    return score / (2 * ITERS)

# print("hello")
# print(calc_equity(["As", "2s"], None, [], phase=0))


def hand_rank(my_cards, board_cards):
    """
    Given hole cards and community cards, returns the current hand rank along with highest card in that rank
    """

    total_cards = my_cards + board_cards

    ranks = {}
    suits = {}
    for card in total_cards:
        if card[0] not in ranks:
            ranks[card[0]] = 1
        else:
            ranks[card[0]] += 1
        if card[1] not in suits:
            suits[card[1]] = 1
        else:
            suits[card[1]] += 1
    

    # First do rank logic. This includes: pairs/trips/quads, straights, full houses
    num_pairs = 0
    trips = False
    quads = False
    full_house = False
    straight = False
    last_rank = -1
    straight_count = 0
    for rank, count in sorted(ranks.items(), key=lambda x: x[0]): # TODO: figure out highest rank logic
        num_rank = rank
        if num_rank == 'K':
            num_rank = 13
        elif num_rank == 'Q':
            num_rank = 12
        elif num_rank == 'J':
            num_rank = 11
        elif num_rank == 'T':
            num_rank = 10
        elif num_rank == 'A':
            num_rank = 1
        else:
            num_rank = int(rank)
        if num_rank == (last_rank+1):
            straight_count += 1
        else:
            straight_count = 1
        last_rank = num_rank
        if count == 2:
            num_pairs += 1
        elif count == 3:
            trips = True
        elif count == 4:
            quads = True
    if last_rank == 13 and 'A' in ranks:
        straight_count += 1
    if trips and num_pairs >= 1:
        full_house = True
    if straight_count >= 5:
        straight = True

    flush = False
    # Then do suit logic. This includes flushes
    for suit, count in suits.items():
        if count >= 5:
            flush = True

    # Ugly logic. Fix later
    if flush and straight: # TODO: Add royal flush support
        return 1
    elif quads:
        return 3
    elif full_house:
        return 4
    elif flush:
        return 5
    elif straight:
        return 6
    elif trips: 
        return 7
    elif num_pairs == 2:
        return 8
    elif num_pairs == 1:
        return 9
    else:
        return 10

def pot_odds(opp_bet, pot_size):
    return (opp_bet / (2*opp_bet + pot_size))