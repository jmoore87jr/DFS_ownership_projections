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
    df['Unnamed: 4'] = df['Unnamed: 4'].map(lambda x: float(x.strip('$').replace(',', '')))
    df['Player, POS'] = df['Player, POS'].map(lambda x: x.split(',', 1)[0])
    # calculate FPts
    df['FPts'] = df['Unnamed: 4'] * df['Proj / $1K.1'] / 1000
    players_and_points = df[['Player, POS', 'FPts']]
    players_and_points.columns = ['Player', 'FPts']
    return players_and_points

def get_sabersim_projections():
    # import .csv and then 
    df = pd.read_csv('rotoballers_full.csv')
    # take player name and FPts columns, then return
    print("Sabersim projections saved.") 
    return players_and_points

def merge_projections_to_DK(site):
    # replace AvgPoints column with projections
    ## dk_sheet = get_dk_salaries()
    dk_sheet = pd.read_csv('dk_salaries.csv') ## delete this and use get_dk_salaries for final script
    if site == 'rotoballer':
        rotoballer_sheet = get_rotoballer_projections()
        new_sheet = pd.merge(dk_sheet, rotoballer_sheet, left_on='Name', right_on='Player')
        new_sheet['AvgPointsPerGame'] = new_sheet['FPts']
        new_sheet.drop(['Player', 'FPts'], axis=1, inplace=True)
        new_sheet.to_csv('rotoballer_projections.csv')
        print("Rotoballer projections saved.")
        return new_sheet 

def main():
    dk_sheet = get_dk_salaries()
    p1 = get_sabersim_projections()
    p2 = get_rotoballer_projections()
    p3 = get_numberfire_projections()
    # merge dk_sheet with p1, save .csv, then feed it to pydfs-lineup-optimizer
    # calculate_exposure() for each player
    # repeat with p2 and p3
    # average the exposures
    # return ownership projections

merge_projections_to_DK('rotoballer')



