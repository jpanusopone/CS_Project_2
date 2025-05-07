CollabGraph: Spotify Artist Collaboration Network
CollabGraph is a Python application that builds and visualizes collaboration networks between music artists using the Spotify Web API.
It calculates an "influence score" for each artist, analyzes connectivity, and generates an interactive graph that users can explore via their web browser.

Features

Fetch artist metadata (popularity, genres, followers) using the Spotify API
Calculate artist influence scores using a log-scaled follower model
Recursively build collaboration graphs across multiple levels
Visualize networks interactively using PyVis (with artist tooltips, genre info, and Spotify links)
Analyze network structure: top influencers and most connected artists
Optional demo mode for faster testing with fewer API calls

Example Output

Interactive HTML graph view of artist collaborations
Console report of:
Top influential artists
Most connected artists
