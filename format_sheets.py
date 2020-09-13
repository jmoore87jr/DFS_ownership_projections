import numpy as np
import pandas as pd
from functools import reduce
import scipy.stats as ss
from collections import defaultdict

# separate ceiling stuff into separate scripts


sites = ['rotogrinders', 'awesemo', 'sabersim']

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

def get_stdev():
    df = pd.read_csv('sabersim_raw.csv').fillna(0)
    df = df[['Name', 'dk_std']]
    d = defaultdict(int)
    for name, std in zip(df['Name'], df['dk_std']):
        d[name] = round(std, 1)
    return d

def average_projections():
    # average the projections from the sites and make ceilings column
    # should probably pass site and go site by site
    dfs = []
    for site in sites:
        get_func = globals()["format_" + site + "_projections"]
        dfs.append(get_func())
    std = get_stdev()
    df = reduce(lambda left, right: pd.merge(left, right, on='Player'), dfs)
    stds = []
    means = []
    ceils = []
    for i,p in enumerate(df['Player']):
        stds.append(std[p])
        #means.append(np.mean([df['FPts_x'][i], df['FPts_y'][i], df['FPts'][i]]))
        means.append(np.mean([df['FPts_x'][i], df['FPts_y'][i]]))
        ceils.append(ss.norm(means[i], std[p]).ppf(0.9))
    df['means'] = means
    df['std'] = stds 
    df['ceil'] = ceils
    return df[['Player', 'ceil']].dropna()

def merge_ceilings_to_DK():
    dk_sheet = pd.read_csv('dk_salaries.csv')
    df = average_projections()
    new_sheet = pd.merge(dk_sheet, df, left_on='Name', right_on='Player')
    new_sheet['AvgPointsPerGame'] = new_sheet['ceil']
    new_sheet.drop(['Player', 'ceil'], axis=1, inplace=True)
    return new_sheet 

def format_and_save(ceil=False): 
    if ceil == True:
        sheet = merge_ceilings_to_DK()
        sheet.to_csv(f'ceilings.csv')
        print(f"ceilings saved.")
    else:
        for site in sites:
            sheet = merge_projections_to_DK(site)
            sheet.to_csv(f'{site}_projections.csv')
            print(f"{site} projections saved.")


get_dk_salaries()
format_and_save(ceil=False)
format_and_save(ceil=True)


