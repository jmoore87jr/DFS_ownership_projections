import numpy as np
import pandas as pd
from collections import defaultdict
from functools import reduce

# create separate function for scraping

nuggets = ['Jamal Murray', 'Nikola Jokic', 'Jerami Grant', 'Gary Harris', 'Paul Millsap', 'Michael Porter Jr', 'Torrey Craig', 'Monte Morris', 'Mason Plumlee']
clippers = ['Kawhi Leonard', 'Ivica Zubac', 'Marcus Morris', 'Paul George', 'Patrick Beverley', 'Louis Williams', 'Landry Shamet', 'Jamychal Green', 'Montrezl Harrell', 'Reggie Jackson']
rockets = ['Russell Westbrook', 'James Harden', 'Eric Gordon', 'Robert Covington', 'P J Tucker', 'Ben McLemore', 'Jeff Green', 'Austin Rivers', 'Danuel House Jr']
lakers = ['Anthony Davis', 'Lebron James', 'Kentavious Caldwell Pope', 'Danny Green', 'Javale Mcgee', 'Rajon Rondo', 'Alex Caruso', 'Kyle Kuzma', 'Markieff Morris']
raptors = ['Marc Gasol', 'Kyle Lowry', 'Pascal Siakam', 'Fred Vanvleet', 'OG Anunoby', 'Norman Powell', 'Serge Ibaka']
celtics = ['Kemba Walker', 'Jayson Tatum', 'Jaylen Brown', 'Marcus Smart', 'Daniel Theis', 'Brad Wanamaker', 'Robert Williams', 'Semi Ojeleye', 'Enes Kanter']
heat = ['Jimmy Butler', 'Goran Dragic', 'Jae Crowder', 'Bam Adebayo', 'Duncan Robinson', 'Tyler Herro', 'Kendrick Nunn', 'Andre Iguodala', 'Kelly Olynyk']
bucks = ['Giannis Antetokounmpo', 'Khris Middleton', 'Brook Lopez', 'Eric Bledsoe', 'Wesley Matthews', 'Donte Divincenzo', 'George Hill', 'Marvin Williams', 'Pat Connaughton', 'Kyle Korver']

pacers = ['Domantas Sabonis', 'T J Warren', 'Malcolm Brogdon', 'Myles Turner', 'Victor Oladipo', 'Justin Holiday', 'Aaron Holiday', 'Doug Mcdermott', 'T J Mcconnell']
sixers = ['Ben Simmons', 'Tobias Harris', 'Josh Richardson', 'Al Horford', 'Joel Embiid', 'Furkan Korkmaz', 'Alec Burks', 'Shake Milton', 'Matisse Thybulle']
nets = ['Spencer Dinwiddie', 'Joe Harris', 'Caris Levert', 'Garrett Temple', 'Jarrett Allen', 'Tyler Johnson']
magic = ['Markelle Fultz', 'Terrence Ross', 'Evan Fournier', 'Nikola Vucevic', 'Aaron Gordon', 'Jonathan Isaac', 'D J Augustin']
thunder = ['Shai Gilgeous Alexander', 'Chris Paul', 'Dennis Schroder', 'Danilo Gallinari', 'Steven Adams', 'Luguentz Dort', 'Terrance Ferguson', 'Darius Bazley', 'Nerlens Noel']
jazz = ['Rudy Gobert', 'Donovan Mitchell', 'Bojan Bogdanovic', 'Joe Ingles', 'Mike Conley', 'Royce Oneale', 'Jordan Clarkson', 'Emmanuel Mudiay', 'Georges Niang']
mavericks = ['Luka Doncic', 'Kristaps Porzingis', 'Dorian Finney Smith', 'Tim Hardaway', 'Dwight Powell', 'Maxi Kleber', 'Seth Curry', 'Delon Wright', 'Boban Marjanovic']
blazers = ['Damian Lillard', 'C J Mccollum', 'Trevor Ariza', 'Carmelo Anthony', 'Hassan Whiteside', 'Gary Trent', 'Anfernee Simons', 'Mario Hezonja']

#players = nuggets + clippers + rockets + lakers + raptors + celtics + heat + bucks
#players = pacers + sixers + nets + magic + thunder + jazz + mavericks + blazers
#players = ['Kyle Lowry', 'Fred Vanvleet', 'OG Anunoby', 'Pascal Siakam', 'Marc Gasol']
#players = ['Jamal Murray', 'Nikola Jokic', 'Jerami Grant', 'Paul Millsap', 'Michael Porter Jr']
#players = ['Kemba Walker', 'Marcus Smart', 'Jaylen Brown', 'Jayson Tatum', 'Daniel Theis']
#players = ['Patrick Beverley', 'Paul George', 'Kawhi Leonard', 'Marcus Morris', 'Ivica Zubac']
players = ['James Harden', 'Russell Westbrook', 'Robert Covington', 'P J Tucker']

def aggregate_stats():
    d = defaultdict()
    d2 = defaultdict()
    for player in players:
        p = player.replace(' ', '-').lower()
        url = 'https://www.numberfire.com/nba/players/daily-fantasy/{}'.format(p)
        try:
            dfs = pd.read_html(url)
        except ImportError:
            print("Import error for {}; check player name.".format(player))
            continue
        if len(dfs) == 4:
            df = pd.read_html(url)[3].dropna()
        elif len(dfs) == 2:
            df = pd.read_html(url)[1].dropna()
        else:
            print("list of dfs length is wrong for {}; check web page.".format(player))
            continue
        # create df2 for stat work below
        df2 = df[['MIN', 'PTS', '3PM-A', 'FTM-A', 'REB', 'AST', 'STL', 'BLK', 'TOV']]
        df = df[['MIN', 'Cost', 'FP']]
        df['Salary'] = [int(c.replace('$', '').replace(',', '')) for c in df['Cost']]
        obs = len(df['Salary'])
        avg_mins = round(np.mean(df['MIN']), 1)
        avg_FP = round(np.mean(df['FP']), 1)
        avg_salary = int(np.mean(df['Salary']))
        avg_value = round(np.mean(avg_FP / avg_salary * 1000), 2)
        # normalize each FP to avg number of minutes
        df['nMIN_ratio'] = round(avg_mins / df['MIN'], 2)
        df['nFP'] = round(df['FP'] * df['nMIN_ratio'])
        print("{}: ".format(p))
        print("Avg. Minutes: {}".format(avg_mins))
        print("Avg. FP: {}".format(avg_FP))
        stdev = round(np.std(df['nFP']), 1)
        stdevpp = round(stdev / avg_FP, 2)
        fppm = round(avg_FP / avg_mins, 2)
        exp_std = round(2.29 * avg_FP**0.393, 1)
        std_diff = round((stdev - exp_std) / exp_std, 4)
        print("Std: {}".format(stdev))
        print("Std/FP: {}".format(stdevpp))
        print(df.info())
        print(df.head())
        d[player] = [obs, avg_mins, avg_salary, avg_FP, stdev, avg_value, fppm, stdevpp, exp_std, std_diff]

        # df2 stats stuff
        threes_made = [int(x.split('-')[0]) for x in df2['3PM-A']]
        fts_made = [int(x.split('-')[0]) for x in df2['FTM-A']]
        avg_ptspm = np.mean(df2['PTS']) / avg_mins
        avg_rebpm = np.mean(df2['REB']) / avg_mins
        avg_astpm = np.mean(df2['AST']) / avg_mins
        avg_3pmpm = np.mean(threes_made) / avg_mins 
        avg_ftmpm = np.mean(fts_made) / avg_mins
        avg_stlpm = np.mean(df2['STL']) / avg_mins
        avg_blkpm = np.mean(df2['BLK']) / avg_mins
        avg_tovpm = np.mean(df2['TOV']) / avg_mins
        d2[player] = [avg_ptspm, avg_rebpm, avg_astpm, avg_3pmpm, avg_ftmpm, avg_stlpm, avg_blkpm, avg_tovpm]

    df = pd.DataFrame.from_dict(d, orient='index', columns=['Observations', 'Avg. Minutes', 'Avg. Salary', 'Avg. FP', 'Std', 'Avg. Value', 'Avg. FP/Min', 'Std/FP', 'Exp. std', 'Std. Diff'])
    df2 = pd.DataFrame.from_dict(d2, orient='index', columns=['Pts/Min', 'Reb/Min', 'Ast/Min', '3PM/Min', 'FTM/Min', 'Stl/Min', 'Blk/Min', 'Tov/Min'])

    print(df)
    print(df2)
    df.to_csv('playoff_players.csv')
    df2.to_csv('playoff_player_stats.csv')


    return [df, df2]

def correlation():
    d = defaultdict()
    for player in players:
        print(player)
        p = player.replace(' ', '-').lower()
        url = 'https://www.numberfire.com/nba/players/daily-fantasy/{}'.format(p)
        try:
            dfs = pd.read_html(url)
        except ImportError:
            print("Import error for {}; check player name.".format(player))
            continue
        if len(dfs) == 4:
            df = pd.read_html(url)[3].dropna()
            dates = pd.read_html(url)[2].Date.dropna() 
        elif len(dfs) == 2:
            df = pd.read_html(url)[1].dropna()
            dates = pd.read_html(url)[0].Date.dropna()
        else:
            print("list of dfs length is wrong for {}; check web page.".format(player))
            continue
        df['Date'] = dates
        df = df[['Date', 'FP']]
        print(df.head())
        print(df.info())
        d[player] = df

    frames = [frame for frame in d.values()]
    result = reduce(lambda left,right: pd.merge(left,right,on='Date'), frames)
    cols = [p for p in d.keys()]
    cols.insert(0, 'Date')
    result.columns = cols
    print(result)
    print(result.corr())
    print("{} observations.".format(len(result.index)))
    result.corr().to_csv('team_corr.csv')


#aggregate_stats()
correlation()