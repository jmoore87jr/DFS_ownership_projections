import numpy as np
import pandas as pd
from collections import defaultdict
import GPP_toy_lineups as lnps
import time

# value is wrong at the end but everything else is right?
# how to build lineups with exposure mirroring pOWN?
# output ownership projection and create differentiation metric (%-based)
# comment calculate_player_winnings() and main()
# build in correlation

start = time.time()


n = 50 # number of lineups to generate
p = 39 # number of ball players
trials = 1000000 # number of GPP trials to run with the lineups you generated

lineups = lnps.optimize_lineups(p, n, random=False) # generate lineups. lineups[0] is preliminary df for re-rolling act_score, lineups[1] is full lineup, lineups[2] is players dict
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
    d2 = defaultdict()
    lineup_names = list(lineups[1].index)
    for i, lineup in enumerate(lineups[1]['lineup']):
        for plyr in lineup:
            if lineups[1]['payout'][i] == 0:
                break
            if plyr not in d.keys():
                d[plyr] = lineups[1]['payout'][i]
            else:   
                d[plyr] += lineups[1]['payout'][i]
        if lineups[1]['payout'][i] == 0:
            break 
        if lineup_names[i] not in d2.keys():
            d2[lineup_names[i]] = lineups[1]['payout'][i]
        else:
            d2[lineup_names[i]] += lineups[1]['payout'][i]
        # store lineup winnings in d2
    return (d, d2)


def main(trials):
    """get player EVs over [trials] trials and average them"""
    ownership = calculate_player_ownership()
    result = defaultdict() # players
    result2 = defaultdict() # lineups
    for t in range(trials):
        winnings = calculate_player_winnings()
        if not result: # store player winnings
            result = winnings[0]
        else:
            for k, v in winnings[0].items():
                if k in result.keys():
                    result[k] += v
                else:
                    result[k] = v
        if not result2: # store lineup winnings
            result2 = winnings[1]
        else:
            for k, v in winnings[1].items():
                if k in result2.keys():
                    result2[k] += v
                else:
                    result2[k] = v
        print("Trial {} complete.".format(t))
    d = defaultdict() # players
    d2 = defaultdict() # lineups
    for k, v in ownership.items(): # players
        if k in result.keys():
            owned = (v/n)*100
            d[k] = ['{}%'.format(round(owned, 2)), result[k], result[k] / (n*(t+1)*owned/100)]
        else:
            d[k] = (0, 0)
    for k in result2.keys(): # lineups
        d2[k] = [lineups[1].lineup[k], result2[k]]
    r = pd.DataFrame.from_dict(d, orient='index', columns=['ownership', 'buyins_won', 'buyins_won/lineup/trial']).fillna(0) # players
    r2 = pd.DataFrame.from_dict(d2, orient='index', columns=['lineup', 'winnings']) # lineups
    r['value'] = [lineups[2][p][3] for p in r.index]
    r['salary'] = [lineups[2][p][1] for p in r.index]
    for k, v in lineups[2].items():
            print("{}: {}".format(k,v))
    print(r.sort_values('buyins_won/lineup/trial', ascending=False))
    print(r2.sort_values('winnings', ascending=False))
    r2.to_csv('lineups_winnings.csv') # lineups
    # lineups DK format, sort by position then remove prefixes
    print("Players owned in any lineup: {} out of {}".format(len(r.index), p))
    print("Buyins_won won by owned players: {}".format(sum(r['buyins_won'])))
    # add total lineup winnings
    # add positions to r

main(trials)
end = time.time()
print("Program took {} seconds.".format(end - start))
