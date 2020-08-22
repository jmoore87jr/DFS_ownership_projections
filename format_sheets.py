import pandas as pd

sites = ['rotogrinders', 'fantasylabs', 'awesemo', 'sabersim']

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
    return players_and_points

def format_fantasylabs_projections():
    df = pd.read_csv('fantasylabs_raw.csv').drop_duplicates()
    players_and_points = df[['Name', 'Projection']]
    players_and_points.columns = ['Player', 'FPts']
    return players_and_points

def format_awesemo_projections():
    df = pd.read_csv('awesemo_raw.csv').drop_duplicates()
    players_and_points = df[['Name', 'Fpts']]
    players_and_points.columns = ['Player', 'FPts']
    return players_and_points

def format_sabersim_projections():
    df = pd.read_csv('sabersim_raw.csv')
    df['SS Projection'] = pd.to_numeric(df['SS Projection'])
    players_and_points = df[['Name', 'SS Projection']]
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
    for site in sites:
        sheet = merge_projections_to_DK(site)
        sheet.to_csv(f'{site}_projections.csv')
        print(f"{site} projections saved.")

# weights based on twitter popularity
# rotogrinders 100k
# labs 50k
# awesemo 20k
# fantasycruncher 15k
# sabersim 10k

get_dk_salaries()
format_and_save()


