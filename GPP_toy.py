"""Generate fake players and prize structure, figure out how to optimize x lineups
and run n trials. Store % of lineups each player is in. Calculate $/lineup for each 
player. WRITE A PLAN FOR HOW TO DO THIS BEFORE STARTING"""

# Plan:
  # this could be a good time to use classes
  # i'm not using positions - annoying to randomly generate and this will make optimization easier
  # use random with list comp to generate dict of {player: [salary, expected_points, actual_points]}
    # can also use random to make sure I have some players with expected pts/$ 6 and some with 4
    # add ownership % to dict.values after simulating lineups
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
    # instructions: https://www.youtube.com/watch?v=cXHvC_FGx24
    # import numpy as np
    # from scipy.optimize import maximize
    # define objective(x) function (sum of expected_points)
    # define functions for each constraint
    # how to create more than 1 lineup?


import math
import pulp as pl
import numpy as np
import pandas as pd
from collections import defaultdict

# approx 10 rotation players per team
# avg salary 5784, stdev 2211
# avg pts/$ 0.005, stdev 0.00052
# avg stdev is 25%...about 18% for s=10k+ and 32% for s=3k
# i'm just setting it equal to 0.25 * points, shouldn't matter here
# avg salary for my players is 6000 (removing < 3000), don't think it matters for testing
# stdev/pts is proportional to sqrt(salary) i.e. s=3000 players have 2x stdev/pts as s=10000

def roundup(x): # round salaries to nearest 100
    return int(math.ceil(x / 100)) * 100

def generate_players(n):
    """Generates dictionary with {player: salary, exp_pts, act_pts}"""
    players = {}
    positions = ['PG', 'SG', 'SF', 'PF', 'C']
    i = 0
    while len(players) < n:
        salary = roundup(np.random.normal(5784, 2211))
        if salary >= 3000: # only take salaries > 3000
            position = np.random.choice(positions)
            exp_pts = np.random.normal(salary*0.005, salary*0.00052)
            act_pts = np.random.normal(exp_pts, 0.25*exp_pts)
            players["p{}".format(i)] = (position, int(salary), int(exp_pts), int(act_pts))
            i += 1
    for k in players.keys():
        print("Players: ")
        print("{}: {}".format(k, players[k]))
    return players

def optimize_lineup(n):
    """Use pulp solver to find the optimal lineup using exp_pts"""
    players = generate_players(n)

    # define problem
    prob = pl.LpProblem('DFS', pl.LpMaximize)

    # set solver
    solver = pl.PULP_CBC_CMD()

    # create decision variables
    player_lineup = [pl.LpVariable('p{}'.format(i), cat='Binary') for i in range(n)]

    # define constraints:
    # sum of the binary player_lineup == 8 players
    prob += (pl.lpSum(player_lineup[i] for i in range(n)) == 8)
    # salary <= 50000
    prob += (pl.lpSum(players['{}'.format(player_lineup[i])][1]*player_lineup[i] for i in range(n)) <= 50000)

    # define objective function:
    # maximize sum of expected_points * player_lineup (binary)
    prob += pl.lpSum(players['{}'.format(player_lineup[i])][2]*player_lineup[i] for i in range(n))

    # solve
    prob.solve(solver)
    pl.LpStatus[prob.status]

    # print results
    d = defaultdict()
    for i,p in enumerate(player_lineup):
        if pl.value(p) == 1:
            d['p{}'.format(i)] = players['p{}'.format(i)]
    results = pd.DataFrame.from_dict(d, orient='index', 
            columns=['Position', 'Salary', 'exp_pts', 'act_pts'])
    print(results)
    print("Total Salary: {}".format(sum(results['Salary'])))
    print("Expected score: {}".format(sum(results['exp_pts'])))
    print("Actual score: {}".format(sum(results['act_pts'])))


optimize_lineup(40)
