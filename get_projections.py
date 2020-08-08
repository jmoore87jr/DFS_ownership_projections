"""Scrape numberfire NBA projections, transform into same .csv style as 
   Draftkings export, and use pydfs-lineup-optimizer to generate lineups"""

import pandas as pd
from pydfs_lineup_optimizer import get_optimizer, Site, Sport

def get_numberfire_projections():
    # get projections from numberfire
    list_of_dfs = pd.read_html('https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections')
    df = list_of_dfs[3]
    ##### add transformation here
    df.to_csv('projections.csv')
    print("numberfire projections saved.")
    return df 

def get_sabersim_projections():
    pass

def get_dk_salaries():
    # have user input DK export URL for a slate, and download the .csv
    url = input("Enter the Draftkings export URL for your slate: ")
    df = pd.read_csv(url)
    df.to_csv('dk_salaries.csv')
    print("Draftkings salaries saved.")
    return df

def get_lineups():
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

def main():
    get_dk_salaries()
    # add projections to dk_salaries sheet here
    get_lineups()

main()
# add exposure capability (guide in pydfs docs)
# get sabersim free trial and check out the format of their projections
# do a vlookup/join type thing to add a projection column to the DK sheet
# delete the AvgPointsPerGame column so projections replace it (keep header?)
# feed the DK sheet with added projections into pydfs_lineup_optimizer

