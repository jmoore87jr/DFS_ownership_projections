"""uses dk_salaries.csv and projections.csv to generate lineups.csv"""

import pandas as pd
from pydfs_lineup_optimizer import get_optimizer, Site, Sport

def generate_lineups():
    # already have dk_salaries.csv saved for test purposes
    n = input("Enter the number of lineups you want: ")
    optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
    optimizer.load_players_from_csv("dk_salaries.csv")
    lineups = []
    headers = ['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F', 'UTIL', 'Pts', 'Salary']
    for lineup in optimizer.optimize(n=n):
        # create list of lineups with pts and salary tacked on
        lineup_list = list(lineup.players)
        lineup_list.append(lineup.fantasy_points_projection)
        lineup_list.append(lineup.salary_costs)
        lineups.append(lineup_list)
    df = pd.DataFrame(lineups, columns=headers)
    df.to_csv('lineups.csv')
    print(f"{n} lineups have been saved.")
    return df

# add exposure capability (guide in pydfs docs)
# do a vlookup/join type thing to add a projection column to the DK sheet
# delete the AvgPointsPerGame column so projections replace it (keep header?)
# feed the DK sheet with added projections into pydfs_lineup_optimizer