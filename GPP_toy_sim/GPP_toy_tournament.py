import numpy as np
import pandas as pd
from collections import defaultdict
import GPP_toy_lineups as lnps
import time

# comment calculate_player_winnings() and main()
# buyins_won/lineup/trial still wrong; right for 100 lineups but not 150
# build in correlation

# time for 20/40/10 without positions: 2.4029
# time for 150/40/1000 without positions: 34.9699
# time for 20/40/10 with position constraints: 

start = time.time()


n = 150 # number of lineups to generate
p = 40 # number of random players to generate
trials = 1000000 # number of GPP trials to run with the lineups you generated

lineups = lnps.optimize_lineups(p, n) # generate lineups. lineups[0] is preliminary df for re-rolling act_score, lineups[1] is full lineup, lineups[2] is players dict
### rename all these lineup returns into something friendly

def reroll_act_pts(): # is this re-rolling same values (for one lineup) n times instead of diff for each lineup? yes
    """For each trial, each player's expected points and stdev stay the same, but the actual points need to be re-run"""
    full_lineups = lineups[1]
    all_act_scores = []
    for l in full_lineups['lineup']:
        act_score = []
        for p in l:
            exp = lineups[2][p][2]
            roll = np.random.normal(exp, (0.37 - 0.0035*exp) * exp)
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
    first = prizepool * 0.96 # first gets 90%
    others = (prizepool * 0.04) / (places_paid - 1) # the rest share remainder
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
    for i, lineup in enumerate(lineups[1]['lineup']):
        for plyr in lineup:
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
        print("Trial {} complete.".format(t))
    d = defaultdict()
    for k, v in ownership.items():
        if k in result.keys():
            owned = (v/n)*100
            d[k] = ['{}%'.format(round(owned, 2)), result[k], result[k] / (n*(t+1)*owned/100)]
        else:
            d[k] = (0, 0)
    r = pd.DataFrame.from_dict(d, orient='index', columns=['ownership', 'buyins_won', 'buyins_won/lineup/trial']).fillna(0)
    print(r.sort_values('buyins_won/lineup/trial', ascending=False))
    r['value'] = [lineups[2][p][3] for p in r.index]
    r['salary'] = [lineups[2][p][1] for p in r.index]
    for k, v in lineups[2].items():
            print("{}: {}".format(k,v))
    print(r.sort_values('buyins_won/lineup/trial', ascending=False))
    print("Players owned in any lineup: {} out of {}".format(len(r.index), p))
    print("Buyins_won won by owned players: {}".format(sum(r['buyins_won'])))

main(trials)
end = time.time()
print("Program took {} seconds.".format(end - start))
