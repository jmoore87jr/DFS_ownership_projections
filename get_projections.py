"""get the DraftKings export sheet for a given slate.
   get projections from various sites and save them in .csv."""

import pandas as pd

def get_dk_salaries():
    # have user input DK export URL for a slate, and download the .csv
    url = input("Enter the DraftKings export URL for your slate: ")
    df = pd.read_csv(url)
    df.to_csv('dk_salaries.csv')
    print("DraftKings salaries saved.")
    return df
    

def get_numberfire_projections():
    # think this is getting fanduel projections...
    # guess we need to calculate from DK scoring later on
    list_of_tables = pd.read_html('https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections')
    df = list_of_tables[3]
    for row in range(1,len(df.index)): # separate names out of 2nd column
        name_field = df.iloc[row,1]
        split_field = str(name_field).split()
        # remove OUT and GTD statuses
        statuses = ['OUT', 'GTD']
        [split_field.remove(status) for status in split_field if status in statuses]
        #### calculate DK points here
        # grab player names of various lengths
        if (len(split_field) == 10):
            name = f"{split_field[2]} {split_field[3]}"
        elif (len(split_field) == 11):
            name = f"{split_field[2]} {split_field[3]} {split_field[4]}"
        elif (len(split_field) == 12):
            name = f"{split_field[3]} {split_field[4]} {split_field[5]}"
        elif (len(split_field) == 14):
            name = f"{split_field[4]} {split_field[5]} {split_field[6]} {split_field[7]}"
        df.iloc[row,1] = name
    players_and_points = df.iloc[:,[1,2]]
    players_and_points.to_csv('numberfire_projections.csv')
    print("numberfire projections saved.")
    return players_and_points
    

def get_rotoballer_projections():
    df = pd.read_csv('rotoballers_full.csv')
    # format salary and player name
    df['▴'] = df['▴'].map(lambda x: float(x.strip('$').replace(',', '')))
    df['Player, POS'] = df['Player, POS'].map(lambda x: x.split(',', 1)[0])
    # calculate FPts
    df['FPts'] = df['▴'] * df['Proj / $1K.1'] / 1000
    players_and_points = df[['Player, POS', 'FPts']]
    players_and_points.columns = ['Player', 'FPts']
    players_and_points.to_csv('rotoballers_full.csv')
    print("Rotoballers projections saved.")
    return players_and_points

def join_projections_to_DK(site):
    # replace AvgPoints column with projections
    pass


#get_dk_salaries()
#get_numberfire_projections()
get_rotoballer_projections()




