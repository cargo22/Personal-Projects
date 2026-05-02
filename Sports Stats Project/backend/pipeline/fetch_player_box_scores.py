# fetch_player_box_scores.py — fetches individual player box scores from the NBA API
# loops through every active player and every target season, inserting stats into PostgreSQL
# this is slow by design — we sleep between API calls to avoid getting blocked by the NBA

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
from datetime import datetime

# playergamelog fetches a player's game-by-game stats for a given season
from nba_api.stats.endpoints import playergamelog

# our PostgreSQL connection tools
from db_connection import SessionLocal, engine
import db_tables

# creates PostgreSQL tables if they don't exist — safe to run even if tables already exist
db_tables.Base.metadata.create_all(bind=engine)

# the seasons we want to fetch box scores for
SEASONS_TO_FETCH = ["2010-11", "2011-12", "2012-13", "2013-14", "2014-15", "2015-16", "2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]

# browser-like headers to avoid getting blocked by the NBA API
# without these, the NBA's servers reject requests that look like bots
HEADERS = {
    'Host': 'stats.nba.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.nba.com/',
    'Origin': 'https://www.nba.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
}


def player_already_synced(db, player, season):
    # returns True if we already have box scores for this player + season combination
    count = db.query(db_tables.PlayerBoxScore).join(db_tables.Game).filter(
        db_tables.PlayerBoxScore.player_id == player.id,
        db_tables.Game.season == season
    ).count()
    return count > 0


def sync_player_box_scores():
    db = SessionLocal()
    total_box_scores = 0
    total_games = 0
    api_calls = 0

    all_players = db.query(db_tables.Player).all()
    all_players = [p if not isinstance(p, tuple) else p[0] for p in all_players]

    print(f"  Found {len(all_players)} players.")

    RECENT_SEASONS = {"2020-21", "2021-22", "2022-23", "2023-24", "2024-25"}

    for i, player in enumerate(all_players):

        # retired players drafted before 2000 couldn't have played in 2010-11 — skip them entirely
        if not player.is_active and (player.draft_year is None or player.draft_year < 2000):
            continue

        # retired players only get fetched for pre-2020 seasons from their draft year onwards
        if player.is_active:
            eligible_seasons = SEASONS_TO_FETCH
        else:
            eligible_seasons = [
                s for s in SEASONS_TO_FETCH
                if s not in RECENT_SEASONS and int(s[:4]) >= player.draft_year
            ]

        seasons_needed = [
            s for s in eligible_seasons
            if not player_already_synced(db, player, s)
        ]

        # skip this player entirely if all seasons are already in the database
        if not seasons_needed:
            print(f"  [{i+1}/{len(all_players)}] {player.name} already synced, skipping...")
            continue

        print(f"  [{i+1}/{len(all_players)}] {player.name} - fetching {seasons_needed}...")

        for season in seasons_needed:
            try:
                # hit the NBA API for this player's game log for this season
                gamelog = playergamelog.PlayerGameLog(
                    player_id=player.nba_player_id,
                    season=season,
                    headers=HEADERS,
                    timeout=100
                )
                games = gamelog.get_normalized_dict()["PlayerGameLog"]
                api_calls += 1

                # sleep after every real API call to avoid getting rate limited
                if games:
                    time.sleep(3.5)

                # take a longer break every 50 calls — the NBA API gets suspicious otherwise
                if api_calls % 50 == 0:
                    print(f"  Taking a 60 second break after {api_calls} API calls...")
                    time.sleep(60)

                for game_data in games:
                    game_id = game_data["Game_ID"]

                    # check if this game already exists in our database
                    game = db.query(db_tables.Game).filter(
                        db_tables.Game.nba_game_id == game_id
                    ).first()

                    # if the game doesn't exist yet, create it from the matchup string
                    if not game:
                        matchup = game_data["MATCHUP"]
                        is_home = "vs." in matchup  # "LAL vs. GSW" means LAL is home

                        if is_home:
                            home_abbr = matchup.split(" vs. ")[0].strip()
                            away_abbr = matchup.split(" vs. ")[1].strip()
                        else:
                            away_abbr = matchup.split(" @ ")[0].strip()
                            home_abbr = matchup.split(" @ ")[1].strip()

                        home_team = db.query(db_tables.Team).filter(
                            db_tables.Team.abbreviation == home_abbr
                        ).first()
                        away_team = db.query(db_tables.Team).filter(
                            db_tables.Team.abbreviation == away_abbr
                        ).first()

                        if home_team and away_team:
                            game = db_tables.Game(
                                nba_game_id=game_id,
                                date=datetime.strptime(
                                    game_data["GAME_DATE"], "%b %d, %Y"
                                ).date(),
                                home_team_id=home_team.id,
                                away_team_id=away_team.id,
                                season=season,
                                is_playoffs=False,
                            )
                            db.add(game)
                            db.flush()  # flush so game.id is available immediately below
                            total_games += 1

                    if not game:
                        continue

                    # skip if we already have this player's box score for this game
                    existing = db.query(db_tables.PlayerBoxScore).filter(
                        db_tables.PlayerBoxScore.player_id == player.id,
                        db_tables.PlayerBoxScore.game_id == game.id
                    ).first()
                    if existing:
                        continue

                    # figure out which team this player was on using the matchup string
                    player_team_abbr = game_data["MATCHUP"].split(" ")[0].strip()
                    team = db.query(db_tables.Team).filter(
                        db_tables.Team.abbreviation == player_team_abbr
                    ).first()

                    # build the box score row and add it to the session
                    box_score = db_tables.PlayerBoxScore(
                        player_id=player.id,
                        game_id=game.id,
                        team_id=team.id if team else None,
                        points=game_data.get("PTS"),
                        rebounds=game_data.get("REB"),
                        assists=game_data.get("AST"),
                        steals=game_data.get("STL"),
                        blocks=game_data.get("BLK"),
                        turnovers=game_data.get("TOV"),
                        personal_fouls=game_data.get("PF"),
                        fgm=game_data.get("FGM"),
                        fga=game_data.get("FGA"),
                        fg3m=game_data.get("FG3M"),
                        fg3a=game_data.get("FG3A"),
                        ftm=game_data.get("FTM"),
                        fta=game_data.get("FTA"),
                        plus_minus=game_data.get("PLUS_MINUS"),
                    )
                    db.add(box_score)
                    total_box_scores += 1

                db.commit()

            except Exception as e:
                print(f"    Error fetching {player.name} {season}: {e}")
                db.rollback()
                time.sleep(5)  # short pause before retrying the next player
                continue

    print(f"\nGames added: {total_games}")
    print(f"Box scores added: {total_box_scores}")
    print(f"Total API calls made: {api_calls}")
    db.close()


# only runs if you execute this file directly: python fetch_player_box_scores.py
if __name__ == "__main__":
    print("Starting sync...")
    sync_player_box_scores()
    print("\nSync complete.")
