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