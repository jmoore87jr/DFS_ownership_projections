**NAME**\
DFS Ownership Projection Calculator

**WHAT**\
Since most DFS players in 2020 are using good projections to make their lineups, I generate ownership projections by taking projections from various sites, optimizing 100 lineups with each of them, and calculating the average ownership for each player. 

**WHY**\
I find many of the ownership projections online to be innacurate. 

**HOW IT WORKS**\
The 'get' functions in get_projections.py take DFS projection tables from various websites, munges them, and returns a 2-column pd.DataFrame of 'Player' and 'FPts'. I was able to scrape from numberfire but it's easier to download from Rotoballers and Sabersim and save the .csv's locally before running the script.

These projections are then joined to the DK export .csv, which pydfs-lineup-optimizer uses to generate 100 optimal lineups. For each set of optimal lineups, the average ownership of each player is calculated and saved in a 2-column pd.DataFrame of 'Player' and 'Ownership'. We can then average the ownership for each player from each set of lineups and return our 'Projected ownership' table.

**HOW TO USE IT**\
Player projection tables from Rotoballers and Sabersim should be saved in your project folder as 'rotoballers_full.csv' and 'sabersim_full.csv', respectively. The program will download and save numberfire projections for you.

Run the program.

When prompted, enter the url of the DraftKings export file for the slate you want to play. 

The .csv of ownership projections will be saved as 'ownership_projections.csv'.

**NOTES**\
The project is not complete yet. If you run it now, it will optimize lineups for season average points, not projected points. 

Upcoming changes:

* Join projections to the DraftKings export sheet
* Generate n lineups from each site
* Calculate average ownership for each player
