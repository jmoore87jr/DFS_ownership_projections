import numpy as np
import pandas as pd
from collections import defaultdict
import GPP_toy_lineups as lnps

# adjust stdev for 3k vs. 10k

n = 100 # number of lineups to generate
p = 40 # number of random players to generate
lineups = lnps.optimize_lineups(p, n) # generate lineups. lineups[1] is full lineup, lineups[0] is preliminary df for re-rolling act_score
# lineups[2] is players dict
# rename these variables
trials = 100

def reroll_act_pts(): # is this re-rolling same values (for one lineup) n times instead of diff for each lineup? yes
    full_lineups = lineups[1]
    all_act_scores = []
    for l in full_lineups['lineup']:
        act_score = []
        for p in l:
            exp = lineups[2][p][2]
            roll = np.random.normal(exp, exp*0.25)
            act_score.append(roll)
        all_act_scores.append(sum(act_score))
    return all_act_scores



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
    return result
    

def calculate_player_winnings(): # add re-roll here
    """Add up all the money each player has won across all lineups, then divide by his lineup count"""
    lineups[1]['score'] = reroll_act_pts() # re-roll points and sort
    lineups[1] = lineups[1].sort_values('score', ascending=False)
    lineups[1]['payout'] = generate_prizepool(n) # add prizepool
    d = defaultdict()
    for i, _ in enumerate(lineups[1]):
        for plyr in lineups[1]['lineup'][i]:
            if lineups[1]['payout'][i] == 0:
                break
            if plyr not in d.keys():
                d[plyr] = lineups[1]['payout'][i]
            else:   
                d[plyr] += lineups[1]['payout'][i]
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
    d = defaultdict()
    for k, v in ownership.items():
        if k in result.keys():
            d[k] = ('{}%'.format(round((v/n)*100), 1), result[k] / t / (n*(v/n)))
        else:
            d[k] = (0, 0)
    r = pd.DataFrame.from_dict(d, orient='index', columns=['ownership', 'buyins_won/contest/lineup'])
    for k, v in lineups[2].items():
            print("{}: {}".format(k,v))
    print(r)
    print(sum(r['buyins_won/contest/lineup']))


main(trials)
#reroll_act_pts()
