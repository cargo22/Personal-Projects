# this file is responsible for loading all the data in our database
# the data is all coming from CSV files in the \data folder
# the data is from the following Kaggle dataset
# https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores/data
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..")) # this line tells us where to look for the following imports by increasing the scope of folders to look in

# this is saying, 'since we are currently in the app root directory, look in pipeline folder, search for these files
# and import those functions'. these functions will load the data into our database
from pipeline.load_games import load_games
from pipeline.load_players import load_players
from pipeline.load_player_box_scores import load_player_box_scores
from pipeline.load_player_box_scores_extended import load_player_box_scores_extended
from pipeline.load_team_box_scores import load_team_box_scores
from pipeline.load_team_box_scores_extended import load_team_box_scores_extended
from pipeline.load_awards import load_awards

# run this code if this file is being executed
if __name__ == "__main__":
    print("Starting full CSV load...")
    load_games()
    load_players()
    load_player_box_scores()
    load_player_box_scores_extended()
    load_team_box_scores()
    load_team_box_scores_extended()
    load_awards()
    print("\nDone.")
