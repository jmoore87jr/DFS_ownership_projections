"""uses dk_salaries.csv and projections.csv to generate lineups.csv"""

import pandas as pd
from pydfs_lineup_optimizer import get_optimizer, Site, Sport

def generate_lineups():
    site = input("Enter the site: ")
    n = int(input("Enter the number of lineups you want: "))
    optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
    optimizer.load_players_from_csv(f'{site}_projections.csv')
    lineups = []
    headers = ['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F', 'UTIL', 'Pts', 'Salary']
    for lineup in optimizer.optimize(n=n):
        # create list of lineups with pts and salary tacked on
        lineup_list = list(lineup.players)
        lineup_list.append(lineup.fantasy_points_projection)
        lineup_list.append(lineup.salary_costs)
        lineups.append(lineup_list)
    df = pd.DataFrame(lineups, columns=headers)
    print(df['PG'].value_counts())
    #df.to_csv(f'{site}_lineups.csv')
    #print(f"{n} lineups have been saved to {site}_lineups.csv")

    # lineup outputs names with position and team
    # do I need to separate out names? 
    # I guess not since they'll be the same on all 3 sheets
    # At the end we need to deal with the DK upload sheet but that's later
    # and can maybe just be done in sheets. we'll see.
    return df

def calculate_exposure():
    # return pd.DataFrame of players and the % of lineups they are in
    # counter dictionary for occurences in DataFrame?
    pass

def main():
    pass

# get sabersim projections and join them to DK sheet AvgPointsPerGame col
  # sabersim ownership projections seem terrible?
# feed the DK sheet with added projections into pydfs_lineup_optimizer
# add exposure capability (guide in pydfs docs)
"""for better ownership projections, generate 100 optimal lineups for 
various sites and average the ownership. this will be the main function 
of our script now."""

generate_lineups()