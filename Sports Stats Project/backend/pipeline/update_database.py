# the sole responsibility of this file is to check if the kaggle database is on the most current version, then update it if not
# the necessary imports so that we know where we are in the directory
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from db_connection import engine

# importing the 2 important functions required to update the databse
# fetching the version number, and updating, as well as loading it onto our PostgreSQL database
from pipeline.fetch_kaggle_data import fetch_kaggle_data
from pipeline.load_all import load_all

if __name__ == "__main__":
    if (fetch_kaggle_data()):
        # checking if the database already has box scores — if it's empty (a fresh
        # machine/rebuild), we need the full history, not just the recent-games shortcut
        with engine.connect() as conn:
            existing_box_scores = conn.execute(text("SELECT COUNT(*) FROM player_box_scores")).scalar()

        database_already_populated = existing_box_scores > 0
        load_all(recent_only=database_already_populated)
    else:
        print("No update needed")