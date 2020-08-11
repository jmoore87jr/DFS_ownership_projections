**NAME**\
DFS Ownership Projection Calculator (NBA only right now)

**WHAT**\
Since most DFS players in 2020 are using good projections to make their lineups, I generate ownership projections by taking projections from various sites, optimizing 100 lineups with each of them, and calculating the average ownership for each player. 

**WHY**\
I find many of the ownership projections online to be innacurate. 

**HOW IT WORKS**\
The 'get' functions in get_projections.py take DFS projection tables from various websites, munges them, and returns a 2-column pd.DataFrame of 'Player' and 'FPts'. I was able to scrape from numberfire but it's easier to download from Rotoballers and Sabersim and save the .csv's locally before running the script.

These projections are then joined to the DK export .csv, which pydfs-lineup-optimizer uses to generate 100 optimal lineups. For each set of optimal lineups, the average ownership of each player is calculated and saved in a 2-column pd.DataFrame of 'Player' and 'Ownership'. We can then average the ownership for each player from each set of lineups and return our 'Projected ownership' table.

**HOW TO USE IT**\
Scraping has been blocked or problematic everywhere. 

1. Go to each site and download or copy/paste the projections in your project folder as {site_name}_raw.csv. Leave them as they are on the site; the program will format them.

2. Run format_sheets.py

When prompted, enter the url of the DraftKings export file for the slate you want to play. 

The .csv of ownership projections will be saved as 'ownership_projections.csv'.

3. Run generate_lineups.py

Enter the sites you want to use, separated by comma. i.e.:
'Enter the sites to be used: sabersim, rotoballer, numberfire'

Then enter the number of lineups to generate from each site, wait a few seconds (150 lineups per site will probably take 2-3 minutes), and you should have your ownership projections saved in the project folder.


**PLANNED CHANGES**
* Add support for other paid sites like  FantasyLabs and Awesemo. The ownership projections are already alright, but adding more pay sites should make them much better.
