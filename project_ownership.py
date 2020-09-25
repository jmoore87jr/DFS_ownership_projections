import pandas as pd
from pydfs_lineup_optimizer import get_optimizer, Site, Sport
from collections import defaultdict
import scipy.stats as ss

sites = ['rotogrinders', 'awesemo', 'sabersim']
weights = {'rotogrinders': 0.4, 'awesemo': 0.3, 'sabersim': 0.3}

def generate_lineups(site, n):
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
    return pd.DataFrame(lineups, columns=headers)

def generate_ceilings_lineups(n):
    optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
    optimizer.load_players_from_csv(f'ceilings.csv')
    lineups = []
    headers = ['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F', 'UTIL', 'Pts', 'Salary']
    for lineup in optimizer.optimize(n=n):
        # create list of lineups with pts and salary tacked on
        lineup_list = list(lineup.players)
        lineup_list.append(lineup.fantasy_points_projection)
        lineup_list.append(lineup.salary_costs)
        lineups.append(lineup_list)
    df = pd.DataFrame(lineups, columns=headers)
    df.to_csv('ceilings_lineups.csv')
    df = df[['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F', 'UTIL']]
    for col in df.columns:
        df[col] = df[col].apply(lambda x: ' '.join(str(x).split()[:-2]))
    df.to_csv('ceilings_upload.csv')
    exposure = df.stack().value_counts()
    exposure.to_csv('exposure.csv')
    print(df)
    return df

def get_player_projections():
    df = pd.read_csv(f'{sites[0]}_projections.csv')
    d = defaultdict(list)
    for i,name in enumerate(df['Name']): # make dictionary w/ empty lists
        d[name] = []
    for site in sites: # fill list
        df = pd.read_csv(f'{site}_projections.csv') 
        for i,name in enumerate(df['Name']):
            d[name].append(df['AvgPointsPerGame'][i])
    # average (better than weights for projections I think)
    d2 = defaultdict(int)
    for k,v in d.items():
        d2[k] = sum(v) / len(v)
    return d2

def get_player_salaries():
    df = pd.read_csv('sabersim_projections.csv')
    df = df[['Name', 'Salary']]
    d = defaultdict(int)
    for name, salary in zip(df['Name'], df['Salary']):
        d[name] = int(salary)
    return d

def get_positions():
    # list each player once for each position, then add constraint where you can't play same player > 1 time in a lineup
    ###still needs work
    df = pd.read_csv('sabersim_projections.csv')
    df = df[['Name', 'Position']]
    d = defaultdict()
    for name, pos in zip(df['Name'], df['Position']):
        d[name] = pos
    print(d)
    return d

def get_stdev():
    df = pd.read_csv('sabersim_raw.csv').fillna(0)
    df = df[['Name', 'dk_std']]
    d = defaultdict(int)
    for name, std in zip(df['Name'], df['dk_std']):
        d[name] = round(std, 1)
    return d

def real_stdev():
    pass

def calculate_exposure(): # input site names separated by comma, in order rotogrinders, fantasylabs, numberfire, sabersim
    n = int(input("Enter the number of lineups to generate for each site: "))
    projections = get_player_projections()
    salaries = get_player_salaries()
    stdev = get_stdev()
    # add positions, manipulate into dictionary
    positions = get_positions()
    # calculate ownership projections
    exposures = []
    for site in sites:
        df = generate_lineups(site, n)
        pstns = ['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F', 'UTIL']
        counts = df['PG'].value_counts().to_frame()
        # join all the positions on player name so they can be summed
        for pos in pstns[1:]:
            series = df[pos].value_counts().to_frame()
            counts = counts.join(series, how='outer').fillna(0)
        # create and fill the exposure column
        site_exposure = f'{site}_exposure'
        counts[site_exposure] = counts.sum(axis=1) / n
        counts = counts.sort_values(by=[site_exposure], ascending=False)
        print(f"{site} exposures: \n")
        print(counts)
        exposures.append(counts)
    df = pd.concat(exposures).fillna(0)
    # can't figure out how to merge the dataframes and keep ownership from each site
    # so I have to create 2 dictionaries, one with all the values and one with the sum
    d = defaultdict(list)
    list_index = list(df.index)
    for i,name in enumerate(list_index):
        site_sum = 0
        for site in sites:
            col = f'{site}_exposure'
            e = df.loc[df.index == list_index[i], col].sum()
            site_sum += e * weights[site]
        d[str(name)].append(site_sum) # pydfs objects don't behave as keys
    d2 = defaultdict(int)
    for k,v in d.items(): # add third column as another value in this dict
        d2[k] = sum(v)
    d3 = defaultdict(int)
    for name in d2.keys(): # strip names so they match projections
        stripped_name = ' '.join(name.split()[:-2])
        print(positions)
        try:
            pos = positions[stripped_name]
        except KeyError:
            print("Name error for {}".format(stripped_name))
            continue # am I missing a bunch of players here?
        proj = projections[stripped_name]
        sal = salaries[stripped_name]
        val = projections[stripped_name] / (salaries[stripped_name]+0.1) * 1000
        std = stdev[stripped_name]
        ceil = ss.norm(projections[stripped_name], stdev[stripped_name]).ppf(0.9)
        d3[stripped_name] = [pos, round(d2[name], 2), round(val, 2), round(proj, 2), sal, 
                            round(std / (proj+0.1) * 10, 2), round(ceil, 2),
                            round(ceil / sal * 1000, 2)]
    # convert back into DataFrame
    results = pd.DataFrame.from_dict(d3, orient='index', 
              columns=['position', 'lineup_%', 'value', 'pts', 'salary', 'stdev/pts', 'ceiling', 'ceiling value']).sort_values(by=['lineup_%'], 
              ascending=False)
    results['projected_ownership'] = round(-0.196651 + results['lineup_%']*0.160766 + results['value']*0.048588 + results['salary']*0.000013, 2)
    print(results)
    results.to_csv('ownership_projections.csv')
    print("Ownership projections saved.")

calculate_exposure()
print(generate_ceilings_lineups(100))
