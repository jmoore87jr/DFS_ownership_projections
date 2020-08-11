"""get the DraftKings export sheet for a given slate.
   get projections from various sites and save them in .csv."""

import pandas as pd

def get_dk_salaries(): # user inputs DK export URL for a slate, .csv is downloaded
    url = input("Enter the DraftKings export URL for your slate: ")
    df = pd.read_csv(url)
    df.to_csv('dk_salaries.csv')
    print("DraftKings salaries saved.")
    return df

def format_rotogrinders_projections():
    df = pd.read_csv('rotogrinders_raw.csv')
    players_and_points = df[['name', 'fpts']]
    players_and_points.columns = ['Player', 'FPts']
    print(players_and_points.info())
    print(players_and_points.head())
    return players_and_points

def format_sabersim_projections():
    df = pd.read_csv('sabersim_raw.csv')
    df['SS Projection'] = pd.to_numeric(df['SS Projection'])
    players_and_points = df[['Name', 'SS Projection']]
    players_and_points.columns = ['Player', 'FPts']
    return players_and_points
    
def format_numberfire_projections():
    # think this is getting fanduel projections...
    # we need to change this by hand because 3pm isn't in the sheet
    #list_of_tables = pd.read_html('https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections')
    #df = list_of_tables[3]
    df = pd.read_csv('numberfire_raw.csv')
    for row in range(1,len(df.index)): # separate names out of 2nd column
        name_field = df.iloc[row,1]
        split_field = str(name_field).split()
        # remove OUT and GTD statuses
        #statuses = ['OUT', 'GTD']
        statuses = ['OUTTue', 'GTDTue']
        [split_field.remove(status) for status in split_field if status in statuses]
        # grab player names of various lengths
        # field sizes for scraping are 10,11,12,14
        # field sizes for copy/paste are 6,7,8
        if (len(split_field) == 6):
            name = f"{split_field[0]} {split_field[1]}"
        elif (len(split_field) == 7):
            name = f"{split_field[0]} {split_field[1]} {split_field[2]}"
        elif (len(split_field) == 8):
            name = f"{split_field[0]} {split_field[1]} {split_field[2]} {split_field[3]}"
        elif (len(split_field) == 10):
            name = f"{split_field[2]} {split_field[3]}"
        elif (len(split_field) == 11):
            name = f"{split_field[2]} {split_field[3]} {split_field[4]}"
        elif (len(split_field) == 12):
            name = f"{split_field[3]} {split_field[4]} {split_field[5]}"
        elif (len(split_field) == 14):
            name = f"{split_field[4]} {split_field[5]} {split_field[6]} {split_field[7]}"
        # testing
        else:
            print(len(split_field))
            print(split_field)
        df.iloc[row,1] = name
    players_and_points = df.iloc[:,[1,2]]
    players_and_points.columns = ['Player', 'FPts']
    return players_and_points

def format_fantasylabs_projections():
    pass 

def format_rotoballer_projections():
    df = pd.read_csv('rotoballer_raw.csv')
    # format salary and player name
    df['Unnamed: 4'] = df['Unnamed: 4'].map(lambda x: float(x.strip('$').replace(',', '')))
    df['Player, POS'] = df['Player, POS'].map(lambda x: x.split(',', 1)[0])
    # calculate FPts
    df['FPts'] = df['Unnamed: 4'] * df['Proj / $1K.1'] / 1000
    players_and_points = df[['Player, POS', 'FPts']]
    players_and_points.columns = ['Player', 'FPts']
    return players_and_points

def merge_projections_to_DK(site): 
    # replace AvgPoints column with projections on DraftKings export sheet
    dk_sheet = pd.read_csv('dk_salaries.csv')
    get_func = globals()["format_" + site + "_projections"]
    sheet = get_func()
    new_sheet = pd.merge(dk_sheet, sheet, left_on='Name', right_on='Player')
    new_sheet['AvgPointsPerGame'] = new_sheet['FPts']
    new_sheet.drop(['Player', 'FPts'], axis=1, inplace=True)
    return new_sheet 

def format_and_save(): # input site names separated by comma
    sites = input("Which sites are being formatted? ").replace(',', '').split()
    for site in sites:
        sheet = merge_projections_to_DK(site)
        sheet.to_csv(f'{site}_projections.csv')
        print(f"{site} projections saved.")

## rotoballer projections seem really terrible, don't use them
## add labs and rotogrinders

#get_dk_salaries()
format_and_save()



