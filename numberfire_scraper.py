"""Scrape numberfire NBA projections, transform into same .csv style as 
   Draftkings export, and use pydfs-lineup-optimizer to generate lineups"""

import pandas as pd

def scrape():
    # scrape projections from numberfire
    list_of_dfs = pd.read_html('https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections')
    df = list_of_dfs[3]
    ##### add transformation here
    df.to_csv('projections.csv')
    return df 

