# fetch_team_box_scores.py — fetches team box scores and game results from the NBA API
# loops through every team and every target season
# also updates home_score/away_score on the games table so win/loss queries work

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
from datetime import datetime

from nba_api.stats.endpoints import teamgamelog

from db_connection import SessionLocal, engine
import db_tables

db_tables.Base.metadata.create_all(bind=engine)

SEASONS_TO_FETCH = ["2022-23", "2023-24", "2024-25"]

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


def team_season_already_synced(db, team, season):
    count = db.query(db_tables.TeamBoxScore).join(db_tables.Game).filter(
        db_tables.TeamBoxScore.team_id == team.id,
        db_tables.Game.season == season
    ).count()
    return count > 0


def sync_team_box_scores():
    db = SessionLocal()
    total_box_scores = 0
    total_games = 0
    api_calls = 0

    all_teams = db.query(db_tables.Team).all()
    print(f"  Found {len(all_teams)} teams.")

    for i, team in enumerate(all_teams):
        seasons_needed = [
            s for s in SEASONS_TO_FETCH
            if not team_season_already_synced(db, team, s)
        ]

        if not seasons_needed:
            print(f"  [{i+1}/{len(all_teams)}] {team.name} already synced, skipping...")
            continue

        print(f"  [{i+1}/{len(all_teams)}] {team.name} - fetching {seasons_needed}...")

        for season in seasons_needed:
            try:
                log = teamgamelog.TeamGameLog(
                    team_id=team.nba_team_id,
                    season=season,
                    headers=HEADERS,
                    timeout=100
                )
                games = log.get_normalized_dict()["TeamGameLog"]
                api_calls += 1

                if games:
                    time.sleep(3.5)

                if api_calls % 50 == 0:
                    print(f"  Taking a 60 second break after {api_calls} API calls...")
                    time.sleep(60)

                for game_data in games:
                    game_id = game_data["Game_ID"]
                    matchup = game_data["MATCHUP"]
                    is_home = "vs." in matchup

                    game = db.query(db_tables.Game).filter(
                        db_tables.Game.nba_game_id == game_id
                    ).first()

                    if not game:
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
                                date=datetime.strptime(game_data["GAME_DATE"], "%b %d, %Y").date(),
                                home_team_id=home_team.id,
                                away_team_id=away_team.id,
                                season=season,
                                is_playoffs=False,
                            )
                            db.add(game)
                            db.flush()
                            total_games += 1

                    if not game:
                        continue

                    # update game score — each team's side gets filled in as we loop through teams
                    pts = game_data.get("PTS")
                    if pts is not None:
                        if is_home and game.home_score is None:
                            game.home_score = int(pts)
                        elif not is_home and game.away_score is None:
                            game.away_score = int(pts)

                    existing = db.query(db_tables.TeamBoxScore).filter(
                        db_tables.TeamBoxScore.team_id == team.id,
                        db_tables.TeamBoxScore.game_id == game.id
                    ).first()
                    if existing:
                        continue

                    db.add(db_tables.TeamBoxScore(
                        team_id=team.id,
                        game_id=game.id,
                        points=int(pts) if pts is not None else None,
                        rebounds=game_data.get("REB"),
                        assists=game_data.get("AST"),
                        turnovers=game_data.get("TOV"),
                        fgm=game_data.get("FGM"),
                        fga=game_data.get("FGA"),
                        fg3m=game_data.get("FG3M"),
                        fg3a=game_data.get("FG3A"),
                        ftm=game_data.get("FTM"),
                        fta=game_data.get("FTA"),
                    ))
                    total_box_scores += 1

                db.commit()

            except Exception as e:
                print(f"    Error fetching {team.name} {season}: {e}")
                db.rollback()
                time.sleep(5)
                continue

    print(f"\nGames added: {total_games}")
    print(f"Team box scores added: {total_box_scores}")
    print(f"Total API calls: {api_calls}")
    db.close()


if __name__ == "__main__":
    print("Starting sync...")
    sync_team_box_scores()
    print("\nSync complete.")
