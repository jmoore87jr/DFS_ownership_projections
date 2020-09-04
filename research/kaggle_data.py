import numpy as np
import pandas as pd 

# combine player results from all dates into a DataFrame with their stdevs

dates = ['11-27', '11-28', '11-29', '11-30', '12-01', '12-02', '12-04', '12-05', '12-06', 
        '12-12', '12-13', '12-14', '12-16', '12-19', '12-20', '12-22', '12-23', '12-25',
        '12-26']
d = {}
for i, date in enumerate(dates):
    d['df{}'.format(i)] = pd.read_csv('data_warehouse/2017-{}/player_results.csv'.format(date))

df = pd.concat([ v for v in d.values() ])[['Player', 'Salary', 'My Proj', 'Value', 'Score']].dropna()

d_plyr_std = {}
for player in df['Player'].unique():
    temp = df[df['Player'] == player]
    obs = len(temp.index)
    mean_sal = round(np.mean(temp['Salary']), 0)
    exp_pts = round(np.mean(temp['My Proj']), 1)
    std =  round(np.std(temp['Score']), 1)
    stdpp = round(std/exp_pts * 10, 1)
    stdpd = round(std/mean_sal * 10000, 1)
    d_plyr_std[player] = [obs, mean_sal, exp_pts, std, stdpp, stdpd] 

plyr_std = pd.DataFrame.from_dict(d_plyr_std, orient='index', columns=['obs', 'mean_sal', 'exp_pts', 'std', 'std/exp_pts', 'std/$'])

print(plyr_std.head())
print(plyr_std.info())

# save the players with 10+ games to analyze

plyr_std[plyr_std['obs'] > 9].to_csv('stdevs.csv')






