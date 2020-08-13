import pandas as pd
from pydfs_lineup_optimizer import get_optimizer, Site, Sport
from collections import defaultdict

sites = ['rotogrinders', 'fantasylabs', 'numberfire', 'sabersim']
weights = {'rotogrinders': 0.526, 'fantasylabs': 0.263, 'numberfire': 0.158, 'sabersim': 0.053}

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

def get_stdev():
    df = pd.read_csv('sabersim_raw.csv')
    df = df[['Name', 'dk_std']]
    d = defaultdict(int)
    for name, std in zip(df['Name'], df['dk_std']):
        d[name] = int(std)
    return d

def calculate_exposure(): # input site names separated by comma, in order rotogrinders, fantasylabs, numberfire, sabersim
    n = int(input("Enter the number of lineups to generate for each site: "))
    projections = get_player_projections()
    salaries = get_player_salaries()
    stdev = get_stdev()
    # calculate ownership projections
    exposures = []
    for site in sites:
        df = generate_lineups(site, n)
        positions = ['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F', 'UTIL']
        counts = df['PG'].value_counts().to_frame()
        # join all the positions on player name so they can be summed
        for pos in positions[1:]:
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
        d3[stripped_name] = [round(d2[name], 2), 
                            round(projections[stripped_name] / (salaries[stripped_name]+0.1) * 1000, 2),
                            round(projections[stripped_name], salaries[stripped_name], stdev[stripped_name]]
    # convert back into DataFrame
    results = pd.DataFrame.from_dict(d3, orient='index', 
              columns=['projected_ownership', 'value', 'pts', 'salary']).sort_values(by=['projected_ownership'], 
              ascending=False)
    print(results)
    ##results.to_csv('ownership_projections.csv')
    ##print("Ownership projections saved.")

calculate_exposure()

# add sabersim stdev column
# test which weights work best
# test which # of lineups works best
# ownership %s need to be smoothed out; perhaps try a points/$ model?
# people fade huge chalk some, but low-owned stars always get at least 5-10%