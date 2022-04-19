from helpers import calc_equity
import pickle

RANKS = "AKQJT98765432"
SUITS = "chsd"


# with open("handstrengths.pickle", 'rb') as handle:
#     p = pickle.load(handle)

# with open('handstrengths.pickle', 'wb') as handle:
#     pickle.dump(p, handle, protocol=4)
#     input()

ranks = {}
for i, r1 in enumerate(RANKS):
    for r2 in RANKS[i:]:
        for s1 in SUITS:
            for s2 in SUITS:
                card1 = r1 + s1
                card2 = r2 + s2
                if (card1) == (card2) or (card2, card1) in ranks:
                    continue 
                ranks[(card1, card2)] = calc_equity([card1, card2], opp=None, board=[], ITERS=10000, phase=0)
                print(card1, card2, ranks[(card1, card2)])

with open('handstrengths.pickle', 'wb') as handle:
    pickle.dump(ranks, handle, protocol=pickle.HIGHEST_PROTOCOL)