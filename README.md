**NAME**\
DFS Ownership Projection Calculator (DraftKings NBA only right now)

**WHAT**\
Since most DFS players in 2020 are using good player projections to make their lineups, I aggregate the most popular ones and use them to create ownership projections.

**WHY**\
I find many of the ownership projections online to be innacurate. 

**HOW IT WORKS**\
format_sheets.py transforms raw projection tables from the sites into a standard format. These are then merged to the DraftKings export sheet.

In project_ownership.py the altered sheet is fed to pydfs-lineup-optimizer, which generates n optimal lineups from each site's player projections. 

Then, exposure (percentage of lineups containing the player) to each player is calculated for each site, then weighted according to the site's popularity (we use Twitter followers as a proxy for popularity - thanks Chris).

**HOW TO USE IT**\ 

1. Go to each site (RotoGrinders, FantasyLabs, Numberfire, SaberSim) and download the projections into your project folder as {site_name}_raw.csv. Leave them as they are on the site; the program will format them.

2. Run format_sheets.py

When prompted, enter the url of the DraftKings export file for the slate you want to play. csv's will be saved with formatted player projections from each of the 4 sites.

3. Run project_ownership.py

Then enter the number of lineups to generate from each site, hit enter, ownership projections will be saved in the project folder. 100 lineups per site will take a couple minutes.


**PLANNED CHANGES**\
* Jupyter notebook demonstration
* Figure out the correct function to boost ownership projections for high salary players; they typically are never below 5-10% in big GPPs
* It would be lovely to push a button and have all the raw projections in a folder, but the sites don't make it easy! 
