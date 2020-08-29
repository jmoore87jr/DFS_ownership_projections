import numpy as np
import pandas as pd
from collections import defaultdict
import GPP_toy_lineups as lnps

# need to re-roll same players, not use same act_score every time

n = 20 # number of lineups to generate
p = 40 # number of random players to generate
plyrs = lnps.generate_players(p) # generate players
lineups = lnps.optimize_lineups(p, n) # generate lineups
trials = 3

def calculate_player_ownership():
    """Counts the number of times a player occurs in the lineups and returns dictionary with {player: count}.
    Later we will divide the player's $ won by his count"""
    d = defaultdict()
    for lnp in lineups['lineup']: # I think there's a faster way to do a counter dict with collections
        for plyr in lnp:
            if plyr in d.keys():
                d[plyr] += 1
            else:
                d[plyr] = 1
    print(d)
    return d


def generate_prizepool(n):
    """Generates DraftKings-like prize structure for a GPP with n players. Returns list of payouts in terms of buyin = 1.
    The larger GPPs are essentially winner take all, where mincashers get their buyin back and top 0.1% win the rest"""
    places_paid = int(n/10)
    prizepool = n 
    result = []
    first = prizepool * 0.9 # first gets 90%
    others = (prizepool * 0.1) / (places_paid - 1) # the rest share remainder
    while len(result) < n:
        if not result:
            result.append(first) 
        elif len(result) < places_paid:
            result.append(others) 
        else:
            result.append(0)
    print(result)
    return result

def roll_scores():
    # roll the act_score for each player, returns same as generate_players(). need to use this to re-add up lineup scores
    d = plyrs
    for k in plyrs.keys():
        if len(d[k]) < 4:
            d[k].append(np.random.normal(d[k][2], 0.25*d[k][2]))
        else:
            d[k].pop()
            d[k].append(np.random.normal(d[k][2], 0.25*d[k][2]))
    return d

def change_scores():
    """plyrs = roll_scores()
    for i in range(len(lineups['score'])):
        score = 0
        for lineup in plyrs.values():
            #lineups['score'][i] = """
    pass
    

def calculate_player_winnings(): # add re-roll here
    """Add up all the money each player has won across all lineups, then divide by his lineup count"""
    lineups['payout'] = generate_prizepool(n)
    print(lineups)
    d = defaultdict()
    places_paid = int(n/10)
    c = 0
    for i, _ in enumerate(lineups):
        for plyr in lineups['lineup'][i]:
            if lineups['payout'][i] == 0:
                break
            if plyr not in d.keys():
                d[plyr] = lineups['payout'][i]
            else:   
                d[plyr] += lineups['payout'][i]
    print(d)
    return d


def main(trials):
    """get player EVs over [trials] trials and average them"""
    ownership = calculate_player_ownership()
    result = defaultdict()
    for _ in range(trials):
        winnings = calculate_player_winnings()
        if not result:
            result = winnings
        else:
            for k, v in winnings.items():
                if k in result.keys():
                    result[k] += v
                else:
                    result[k] = v
    print(result)

main(trials)

