"""uses dk_salaries.csv and projections.csv to generate lineups.csv"""

import pandas as pd
from pydfs_lineup_optimizer import get_optimizer, Site, Sport
from collections import defaultdict

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

def calculate_exposure(): # input site names separated by comma
    sites = input("Enter the sites to be formatted: ").replace(',', '').split()
    n = int(input("Enter the number of lineups to generate for each site: "))
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
    d = defaultdict(list)
    list_index = list(df.index)
    # can't figure out how to merge the dataframes and keep ownership from each site
    # so I have to create 2 dictionaries, one with all the values and one with the sum
    for i,name in enumerate(list_index):
        for site in sites:
            col = f'{site}_exposure'
            e = df.loc[df.index == list_index[i], col].sum()
            d[str(name)].append(e) # pydfs objects don't behave as keys
    d2 = defaultdict(int)
    for k,v in d.items():
        d2[k] = sum(v) / len(sites)
    # convert back into DataFrame
    results = pd.DataFrame.from_dict(d2, orient='index', 
    columns=['projected_ownership']).sort_values(by=['projected_ownership'], ascending=False)
    print(results)
    results.to_csv('ownership_projections.csv')
    print("Ownership projections saved.")
    return results


# upload raw .csv's to github so people can test

calculate_exposure()

# concat all the exposure columns together, then sumif('Name' = df.index[i])