import numpy as np
import pandas as pd
from collections import defaultdict
import GPP_toy_lineups as lnps

# adjust stdev for 3k vs. 10k

n = 20 # number of lineups to generate
p = 40 # number of random players to generate
plyrs = lnps.generate_players(p) # generate players
lineups = lnps.optimize_lineups(p, n) # generate lineups. lineups[1] is full lineup, lineups[0] is preliminary df for re-rolling act_score
trials = 20

def reroll_act_pts():
    df = lineups[0]
    act_scores = []
    for _ in range(n):
        for i, exp in enumerate(df['exp_pts']):
            df['act_pts'][i] = np.random.normal(exp, exp*0.25)
        act_scores.append(sum(df['act_pts']))
    return act_scores



def calculate_player_ownership():
    """Counts the number of times a player occurs in the lineups and returns dictionary with {player: count}.
    Later we will divide the player's $ won by his count"""
    d = defaultdict()
    for lnp in lineups[1]['lineup']: # I think there's a faster way to do a counter dict with collections
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
    

def calculate_player_winnings(): # add re-roll here
    """Add up all the money each player has won across all lineups, then divide by his lineup count"""
    lineups[1]['score'] = reroll_act_pts() # re-roll points and sort
    lineups[1] = lineups[1].sort_values('score', ascending=False)
    lineups[1]['payout'] = generate_prizepool(n) # add prizepool
    print(lineups[1])
    d = defaultdict()
    for i, _ in enumerate(lineups[1]):
        for plyr in lineups[1]['lineup'][i]:
            if lineups[1]['payout'][i] == 0:
                break
            if plyr not in d.keys():
                d[plyr] = lineups[1]['payout'][i]
            else:   
                d[plyr] += lineups[1]['payout'][i]
    print(d)
    return d


def main(trials):
    """get player EVs over [trials] trials and average them"""
    ownership = calculate_player_ownership()
    result = defaultdict()
    for t in range(trials):
        winnings = calculate_player_winnings()
        if not result:
            result = winnings
        else:
            for k, v in winnings.items():
                if k in result.keys():
                    result[k] += v
                else:
                    result[k] = v
    print(result) # turn these into df or print line by line
    print(ownership)
    d = defaultdict()
    for k, v in ownership.items():
        if k in result.keys():
            d[k] = ('{}%'.format((v/n)*100), result[k] / t / (n*(v/n)))
        else:
            d[k] = (0, 0)
    r = pd.DataFrame.from_dict(d, orient='index', columns=['ownership', '$/contest/lineup'])
    print(r)
    print(sum(r['$/contest/lineup']))


main(trials)

