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
    # get sabersim free trial and check out the format of their projections
    pass

def get_dk_salaries():
    # have user input DK export URL for a slate, and download the .csv
    url = input("Enter the Draftkings export URL for your slate: ")
    df = pd.read_csv(url)
    df.to_csv('dk_salaries.csv')
    print("Draftkings salaries saved.")
    return df




