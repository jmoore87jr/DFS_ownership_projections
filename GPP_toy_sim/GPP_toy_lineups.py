"""Generate fake players and prize structure, figure out how to optimize x lineups
and run n trials. Store % of lineups each player is in. Calculate $/lineup for each 
player. WRITE A PLAN FOR HOW TO DO THIS BEFORE STARTING"""

# Plan:
  # seems like the good lineups are winning too much...I think I either don't use int() for scores or I increase player variance
  # this could be a good time to use classes
  # i'm not using positions - this will make optimization faster and it doesn't matter for toy game purposes
  # use random with list comp to generate dict of {player: [salary, expected_points, actual_points]}
    # can also use random to make sure I have some players with expected pts/$ 6 and some with 4
    # add ownership % to dict.values after simulating lineups
    # can I correlate players somehow?
  # write function to optimize
    # objective: max(expected_points)
    # constraint 1: salary <= 50000
    # constraint 2: players == 8
    # constraint 3: PG >= 1 and PG <= 3
    # constraint 4: SG >= 1 and SG <= 3
    # constraint 5: SF >= 1 and SF <= 3
    # constraint 6: PF >= 1 and PF <= 3
    # constraint 7: C >= 1 and C <= 2
    # constraint 8: ownership - set max and min with ownership projection regression formula


import math
import pulp as pl
import numpy as np
import pandas as pd
from collections import defaultdict

def roundup(x): # round salaries to nearest 100
    return int(math.ceil(x / 100)) * 100

def generate_players(p):
    """Generates dictionary with {player: salary, exp_pts, act_pts}"""
    players = {}
    positions = ['PG', 'SG', 'SF', 'PF', 'C']
    i = 0
    while len(players) < p:
        salary = roundup(np.random.normal(5784, 2211))
        if salary >= 3000: # only take salaries > 3000
            position = np.random.choice(positions)
            exp_pts = np.random.normal(salary*0.005, salary*0.00052)
            act_pts = np.random.normal(exp_pts, exp_pts*0.25)
            exp_ppd = (exp_pts / salary) * 1000
            players["p{}".format(i)] = [position, int(salary), int(exp_pts), round(exp_ppd, 2), int(act_pts)]
            i += 1
    print("Players: ")
    for k in players.keys():
        print("{}: {}".format(k, players[k]))
    return players

def optimize_lineups(p, n):
    """Use pulp solver to find top n optimal lineups using exp_pts from p randomly generated players. Returns 
    DataFrame of the optimal lineups and their actual scores"""

    players = generate_players(p)
    
    high_score = 0
    lnps = defaultdict()

    for _ in range(n):
        # define problem
        prob = pl.LpProblem('DFS', pl.LpMaximize)

        # set solver
        solver = pl.PULP_CBC_CMD()

        # create decision variables
        player_lineup = [pl.LpVariable('p{}'.format(i), cat='Binary') for i in range(p)]

        # define constraints:
        # sum of the binary player_lineup == 8 players
        prob += (pl.lpSum(player_lineup[i] for i in range(p)) == 8)
        # salary <= 50000
        prob += (pl.lpSum(players['{}'.format(player_lineup[i])][1]*player_lineup[i] for i in range(p)) <= 50000)
        # lineup projection less than the previous one
        if high_score:
            prob += (pl.lpSum(players['{}'.format(player_lineup[i])][2]*player_lineup[i] for i in range(p)) <= high_score - 1)

        # define objective function:
        # maximize sum of expected_points * player_lineup (binary)
        prob += pl.lpSum(players['{}'.format(player_lineup[i])][2]*player_lineup[i] for i in range(p))

        # solve
        prob.solve(solver)

        # print results for each lineup
        d = defaultdict()
        for i,plyr in enumerate(player_lineup):
            if pl.value(plyr) == 1:
                d['p{}'.format(i)] = players['p{}'.format(i)]
        results = pd.DataFrame.from_dict(d, orient='index', 
                columns=['Position', 'Salary', 'exp_pts', 'exp_ppd', 'act_pts'])
        total_salary = sum(results['Salary'])
        exp_score = sum(results['exp_pts'])
        act_score = sum(results['act_pts']) 
        print(results)
        print("Total Salary: {}".format(total_salary))
        print("Expected score: {}".format(exp_score))
        print("Actual score: {}".format(act_score))

        # set high_score
        high_score = sum(results['exp_pts'])

        # store lineup
        lnps['lineup_{}'.format(_)] = (list(results.index), act_score)

    # print results  
    result = pd.DataFrame.from_dict(lnps, orient='index', columns=['lineup', 'score']).sort_values('score', ascending=False)
    for k in players.keys():
        print("{}: {}".format(k, players[k]))
    print(result)

    return [results, result, players] # need to return more stuff from here in order to re-roll later and alter 'result'




