import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from sqlalchemy import text
from db_connection import SessionLocal
import db_tables
from pipeline.utils import DATA_DIR, SKIP_GAME_TYPES, CUP_GAME_TYPES, get_season, pad_game_id

# function to load each game in NBA history (will take a while)
def load_games():
    print("\n--- Loading Games ---")
    # creating a live connection to PostgreSQL
    db = SessionLocal()

    # NOTE: the NBA uses a structured ID game format, such that every game's ID has specific prefixes: (002 - regular season, 004 - playoffs, -006 - in-season tournament)
    # thus, 0062 will guarantee us a cup knockout game, regardless of the season
    fixed = db.execute(text("UPDATE games SET is_playoffs = true WHERE nba_game_id LIKE '0062%' AND is_playoffs = false"))
    if fixed.rowcount > 0:
        print(f"  Fixed {fixed.rowcount} in-season tournament game(s)")
    db.commit()

    # getting all the teams
    teams = db.query(db_tables.Team).all()

    # creating a map for every team, with the key being its id
    team_map = {t.nba_team_id: t.id for t in teams}

    # reading the Games.csv file
    df = pd.read_csv(os.path.join(DATA_DIR, "Games.csv"), low_memory=False)

    # extract only the regular season and post season games (skip preseason and all-star games)
    df = df[~df["gameType"].isin(SKIP_GAME_TYPES)]

    seeded = 0
    # iterating through the rows of the csv
    for _, row in df.iterrows():
        # forcing each id to be 10 characters long
        nba_game_id = pad_game_id(row["gameId"])

        # to save time, we will first check if the game is already in our database
        existing = db.query(db_tables.Game).filter(
            db_tables.Game.nba_game_id == nba_game_id
        ).first()

        # if in our database, update missing scores and correct is_playoffs if wrong
        if existing:
            if existing.home_score is None and pd.notna(row.get("homeScore")):
                existing.home_score = int(row["homeScore"])
            if existing.away_score is None and pd.notna(row.get("awayScore")):
                existing.away_score = int(row["awayScore"])

            # defining in-season tournament finals
            is_cup_final = row["gameType"] in CUP_GAME_TYPES and nba_game_id.startswith("0062")

            # making sure in-season tournament finals, play-in games, and playoff games are not counted towards regular season
            correct = row["gameType"] in ("Playoffs", "Play-in Tournament") or is_cup_final
            if existing.is_playoffs != correct:
                existing.is_playoffs = correct
            continue

        # skip cup finals that aren't already in the DB — they don't count as regular season
        if row["gameType"] in CUP_GAME_TYPES:
            continue

        # extracting home team score and away team score
        home_team_id = team_map.get(int(row["hometeamId"])) if pd.notna(row["hometeamId"]) else None
        away_team_id = team_map.get(int(row["awayteamId"])) if pd.notna(row["awayteamId"]) else None

        # only continue if there is a valid score for both teams
        if not home_team_id or not away_team_id:
            continue

        # extracting the game's date
        game_date = pd.to_datetime(row["gameDate"]).date()

        # adding the game to the database
        db.add(db_tables.Game(
            nba_game_id=nba_game_id,
            date=game_date,
            season=get_season(game_date),
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            home_score=int(row["homeScore"]) if pd.notna(row.get("homeScore")) else None,
            away_score=int(row["awayScore"]) if pd.notna(row.get("awayScore")) else None,
            is_playoffs=row["gameType"] in ("Playoffs", "Play-in Tournament"),
        ))
        seeded += 1

        # adding a tracker to see how much progress we've made
        if seeded % 1000 == 0:
            db.commit()
            print(f"  {seeded} games inserted...")

    # save changes
    db.commit()
    print(f"Games inserted: {seeded}")
    db.close()


if __name__ == "__main__":
    # run function when file is executed
    load_games()
