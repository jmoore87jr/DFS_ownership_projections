import numpy as np
import pandas as pd
from collections import defaultdict
import GPP_toy_lineups as lnps
import time

# examine buyins_won/contest/lineup individual parts; seeing some unintuitive results for low owned expensive guys
  # total winnings for 1000 trials should be 20000...calculate winnings / 8 for each player every trial?
# build in correlation

start = time.time()


n = 100 # number of lineups to generate
p = 40 # number of random players to generate
trials = 100 # number of GPP trials to run with the lineups you generated

lineups = lnps.optimize_lineups(p, n) # generate lineups. lineups[1] is full lineup, lineups[0] is preliminary df for re-rolling act_score

# lineups[2] is players dict
# rename these variables

def reroll_act_pts(): # is this re-rolling same values (for one lineup) n times instead of diff for each lineup? yes
    full_lineups = lineups[1]
    all_act_scores = []
    for l in full_lineups['lineup']:
        act_score = []
        for p in l:
            exp = lineups[2][p][2]
            roll = np.random.normal(exp, (0.37 - 0.0035*exp) * exp)
            act_score.append(roll)
        all_act_scores.append(sum(act_score))
    print(all_act_scores)
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
    print("After reroll and payout add: {}".format(lineups[1].head(11)))
    d = defaultdict()
    for i, _ in enumerate(lineups[1]): ### winnings not calculated correctly for 100 lineups instead of 20; not counting all the cashes
        for plyr in lineups[1]['lineup'][i]:
            if lineups[1]['payout'][i] == 0:
                break
            if plyr not in d.keys():
                d[plyr] = lineups[1]['payout'][i]
            else:   
                d[plyr] += lineups[1]['payout'][i]
    print("Player winnings: {}".format(d))
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
        print("Trial result: {}".format(result))
    d = defaultdict()
    for k, v in ownership.items():
        if k in result.keys():
            owned = round((v/n)*100, 1)
            d[k] = ['{}%'.format(owned), result[k], result[k]*(1/owned)/t]
        else:
            d[k] = (0, 0)
    r = pd.DataFrame.from_dict(d, orient='index', columns=['ownership', 'buyins_won', 'buyins_won/lineup/trial'])
    for k, v in lineups[2].items():
            print("{}: {}".format(k,v))
    # normalize buyins_won/contest/lineup
    num_owned = len(r.index)
    raw_won = sum(r['buyins_won'])
    #for i in range(num_owned):
        #r['buyins_won'][i] = r['buyins_won'][i] * (num_owned / raw_won)
    print(r)
    print("Players owned in any lineup: {} out of {}".format(len(r.index), p))
    print("Buyins_won won by owned players: {}".format(sum(r['buyins_won'])))

    # buyins_won/contest/lineup: result[k] / t / (n*(v/n))

main(trials)
end = time.time()
print("Program took {} seconds.".format(end - start))
