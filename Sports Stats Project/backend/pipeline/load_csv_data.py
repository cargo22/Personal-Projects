# load_csv_data.py — loads the Kaggle CSV dataset into PostgreSQL
# covers all NBA games since 1947, updated daily
# run this instead of the slow NBA API pipeline

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from datetime import datetime
from sqlalchemy import text

from db_connection import SessionLocal, engine
import db_tables

db_tables.Base.metadata.create_all(bind=engine)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

SKIP_GAME_TYPES = {"Preseason", "All-Star Game"}
CHUNK_SIZE = 10000


def get_season(date):
    year = date.year if date.month >= 10 else date.year - 1
    return f"{year}-{str(year + 1)[2:]}"


def pad_game_id(game_id):
    return str(int(game_id)).zfill(10)


def load_games():
    print("\n--- Loading Games ---")
    db = SessionLocal()

    # cache all teams by nba_team_id for fast lookup
    teams = db.query(db_tables.Team).all()
    team_map = {t.nba_team_id: t.id for t in teams}

    df = pd.read_csv(os.path.join(DATA_DIR, "Games.csv"), low_memory=False)
    df = df[~df["gameType"].isin(SKIP_GAME_TYPES)]

    seeded = 0
    for _, row in df.iterrows():
        nba_game_id = pad_game_id(row["gameId"])

        existing = db.query(db_tables.Game).filter(
            db_tables.Game.nba_game_id == nba_game_id
        ).first()
        if existing:
            # update scores if missing
            if existing.home_score is None and pd.notna(row.get("homeScore")):
                existing.home_score = int(row["homeScore"])
            if existing.away_score is None and pd.notna(row.get("awayScore")):
                existing.away_score = int(row["awayScore"])
            continue

        home_team_id = team_map.get(int(row["hometeamId"])) if pd.notna(row["hometeamId"]) else None
        away_team_id = team_map.get(int(row["awayteamId"])) if pd.notna(row["awayteamId"]) else None

        if not home_team_id or not away_team_id:
            continue

        game_date = pd.to_datetime(row["gameDate"]).date()

        db.add(db_tables.Game(
            nba_game_id=nba_game_id,
            date=game_date,
            season=get_season(game_date),
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            home_score=int(row["homeScore"]) if pd.notna(row.get("homeScore")) else None,
            away_score=int(row["awayScore"]) if pd.notna(row.get("awayScore")) else None,
            is_playoffs=row["gameType"] == "Playoffs",
        ))
        seeded += 1

        if seeded % 1000 == 0:
            db.commit()
            print(f"  {seeded} games inserted...")

    db.commit()
    print(f"Games inserted: {seeded}")
    db.close()


def load_players():
    print("\n--- Loading Players ---")
    db = SessionLocal()

    df = pd.read_csv(os.path.join(DATA_DIR, "Players.csv"))

    seeded = 0
    for _, row in df.iterrows():
        # derive position from boolean columns
        position = None
        if row.get("guard") == 1:
            position = "G"
        elif row.get("forward") == 1:
            position = "F"
        elif row.get("center") == 1:
            position = "C"

        to_year = int(row["toYear"]) if pd.notna(row.get("toYear")) else None
        is_active = to_year is not None and to_year >= 2024

        existing = db.query(db_tables.Player).filter(
            db_tables.Player.nba_player_id == int(row["personId"])
        ).first()

        if existing:
            existing.draft_year = int(row["draftYear"]) if pd.notna(row.get("draftYear")) else existing.draft_year
            existing.draft_round = int(row["draftRound"]) if pd.notna(row.get("draftRound")) else existing.draft_round
            existing.draft_number = int(row["draftNumber"]) if pd.notna(row.get("draftNumber")) else existing.draft_number
            existing.position = position or existing.position
            existing.is_active = is_active
            continue

        db.add(db_tables.Player(
            nba_player_id=int(row["personId"]),
            name=f"{row['firstName']} {row['lastName']}".strip(),
            first_name=row["firstName"] if pd.notna(row.get("firstName")) else None,
            last_name=row["lastName"] if pd.notna(row.get("lastName")) else None,
            position=position,
            height_inches=int(row["heightInches"]) if pd.notna(row.get("heightInches")) else None,
            weight_lbs=int(row["bodyWeightLbs"]) if pd.notna(row.get("bodyWeightLbs")) else None,
            jersey_number=str(row["jersey"]) if pd.notna(row.get("jersey")) else None,
            birthdate=pd.to_datetime(row["birthDate"]).date() if pd.notna(row.get("birthDate")) else None,
            country=row["country"] if pd.notna(row.get("country")) else None,
            school=row["school"] if pd.notna(row.get("school")) else None,
            draft_year=int(row["draftYear"]) if pd.notna(row.get("draftYear")) else None,
            draft_round=int(row["draftRound"]) if pd.notna(row.get("draftRound")) else None,
            draft_number=int(row["draftNumber"]) if pd.notna(row.get("draftNumber")) else None,
            is_active=is_active,
        ))
        seeded += 1

    db.commit()
    print(f"Players inserted: {seeded}")
    db.close()


def load_player_box_scores():
    print("\n--- Loading Player Box Scores ---")
    db = SessionLocal()

    # cache all games and players for fast lookup
    print("  Building lookup caches...")
    game_map = {g.nba_game_id: g.id for g in db.query(db_tables.Game).all()}
    player_map = {p.nba_player_id: p.id for p in db.query(db_tables.Player).all()}
    team_map = {t.nba_team_id: t.id for t in db.query(db_tables.Team).all()}

    total = 0
    for chunk in pd.read_csv(os.path.join(DATA_DIR, "PlayerStatistics.csv"), chunksize=CHUNK_SIZE, low_memory=False):
        rows_to_insert = []

        for _, row in chunk.iterrows():
            if pd.isna(row.get("personId")) or pd.isna(row.get("gameId")):
                continue
            if pd.isna(row.get("numMinutes")):
                continue
            raw_min = row["numMinutes"]
            try:
                if ":" in str(raw_min):
                    parts = str(raw_min).split(":")
                    minutes_val = int(parts[0]) + int(parts[1]) / 60
                else:
                    minutes_val = float(raw_min)
            except (ValueError, IndexError):
                continue
            if minutes_val == 0:
                continue

            nba_game_id = pad_game_id(row["gameId"])
            game_id = game_map.get(nba_game_id)
            player_id = player_map.get(int(row["personId"]))
            team_id = team_map.get(int(row["playerteamId"])) if pd.notna(row.get("playerteamId")) else None

            if not game_id or not player_id:
                continue

            rows_to_insert.append({
                "player_id": player_id,
                "game_id": game_id,
                "team_id": team_id,
                "points": int(row["points"]) if pd.notna(row.get("points")) else None,
                "rebounds": int(row["reboundsTotal"]) if pd.notna(row.get("reboundsTotal")) else None,
                "assists": int(row["assists"]) if pd.notna(row.get("assists")) else None,
                "steals": int(row["steals"]) if pd.notna(row.get("steals")) else None,
                "blocks": int(row["blocks"]) if pd.notna(row.get("blocks")) else None,
                "turnovers": int(row["turnovers"]) if pd.notna(row.get("turnovers")) else None,
                "personal_fouls": int(row["foulsPersonal"]) if pd.notna(row.get("foulsPersonal")) else None,
                "minutes_played": minutes_val,
                "fgm": int(row["fieldGoalsMade"]) if pd.notna(row.get("fieldGoalsMade")) else None,
                "fga": int(row["fieldGoalsAttempted"]) if pd.notna(row.get("fieldGoalsAttempted")) else None,
                "fg3m": int(row["threePointersMade"]) if pd.notna(row.get("threePointersMade")) else None,
                "fg3a": int(row["threePointersAttempted"]) if pd.notna(row.get("threePointersAttempted")) else None,
                "ftm": int(row["freeThrowsMade"]) if pd.notna(row.get("freeThrowsMade")) else None,
                "fta": int(row["freeThrowsAttempted"]) if pd.notna(row.get("freeThrowsAttempted")) else None,
                "plus_minus": int(row["plusMinusPoints"]) if pd.notna(row.get("plusMinusPoints")) else None,
            })

        if rows_to_insert:
            db.execute(
                text("""
                    INSERT INTO player_box_scores
                    (player_id, game_id, team_id, points, rebounds, assists, steals, blocks,
                     turnovers, personal_fouls, minutes_played, fgm, fga, fg3m, fg3a, ftm, fta, plus_minus)
                    VALUES (:player_id, :game_id, :team_id, :points, :rebounds, :assists, :steals, :blocks,
                            :turnovers, :personal_fouls, :minutes_played, :fgm, :fga, :fg3m, :fg3a, :ftm, :fta, :plus_minus)
                    ON CONFLICT (player_id, game_id) DO UPDATE SET
                        minutes_played = EXCLUDED.minutes_played,
                        points = EXCLUDED.points,
                        rebounds = EXCLUDED.rebounds,
                        assists = EXCLUDED.assists,
                        steals = EXCLUDED.steals,
                        blocks = EXCLUDED.blocks,
                        turnovers = EXCLUDED.turnovers,
                        fgm = EXCLUDED.fgm,
                        fga = EXCLUDED.fga,
                        fg3m = EXCLUDED.fg3m,
                        fg3a = EXCLUDED.fg3a,
                        ftm = EXCLUDED.ftm,
                        fta = EXCLUDED.fta,
                        plus_minus = EXCLUDED.plus_minus
                """),
                rows_to_insert
            )
            db.commit()
            total += len(rows_to_insert)
            print(f"  {total} player box scores inserted...")

    print(f"Player box scores total: {total}")
    db.close()


def load_team_box_scores():
    print("\n--- Loading Team Box Scores ---")
    db = SessionLocal()

    print("  Building lookup caches...")
    game_map = {g.nba_game_id: g.id for g in db.query(db_tables.Game).all()}
    team_map = {t.nba_team_id: t.id for t in db.query(db_tables.Team).all()}

    total = 0
    for chunk in pd.read_csv(os.path.join(DATA_DIR, "TeamStatistics.csv"), chunksize=CHUNK_SIZE, low_memory=False):
        rows_to_insert = []

        for _, row in chunk.iterrows():
            nba_game_id = pad_game_id(row["gameId"])
            game_id = game_map.get(nba_game_id)
            team_id = team_map.get(int(row["teamId"])) if pd.notna(row.get("teamId")) else None

            if not game_id or not team_id:
                continue

            rows_to_insert.append({
                "team_id": team_id,
                "game_id": game_id,
                "points": int(row["teamScore"]) if pd.notna(row.get("teamScore")) else None,
                "rebounds": int(row["reboundsTotal"]) if pd.notna(row.get("reboundsTotal")) else None,
                "assists": int(row["assists"]) if pd.notna(row.get("assists")) else None,
                "turnovers": int(row["turnovers"]) if pd.notna(row.get("turnovers")) else None,
                "fgm": int(row["fieldGoalsMade"]) if pd.notna(row.get("fieldGoalsMade")) else None,
                "fga": int(row["fieldGoalsAttempted"]) if pd.notna(row.get("fieldGoalsAttempted")) else None,
                "fg3m": int(row["threePointersMade"]) if pd.notna(row.get("threePointersMade")) else None,
                "fg3a": int(row["threePointersAttempted"]) if pd.notna(row.get("threePointersAttempted")) else None,
                "ftm": int(row["freeThrowsMade"]) if pd.notna(row.get("freeThrowsMade")) else None,
                "fta": int(row["freeThrowsAttempted"]) if pd.notna(row.get("freeThrowsAttempted")) else None,
                "plus_minus": int(row["plusMinusPoints"]) if pd.notna(row.get("plusMinusPoints")) else None,
                "pts_paint": int(row["pointsInThePaint"]) if pd.notna(row.get("pointsInThePaint")) else None,
                "pts_2nd_chance": int(row["pointsSecondChance"]) if pd.notna(row.get("pointsSecondChance")) else None,
                "pts_fb": int(row["pointsFastBreak"]) if pd.notna(row.get("pointsFastBreak")) else None,
                "largest_lead": int(row["biggestLead"]) if pd.notna(row.get("biggestLead")) else None,
                "lead_changes": int(row["leadChanges"]) if pd.notna(row.get("leadChanges")) else None,
                "times_tied": int(row["timesTied"]) if pd.notna(row.get("timesTied")) else None,
            })

        if rows_to_insert:
            db.execute(
                text("""
                    INSERT INTO team_box_scores
                    (team_id, game_id, points, rebounds, assists, turnovers, fgm, fga, fg3m, fg3a,
                     ftm, fta, plus_minus, pts_paint, pts_2nd_chance, pts_fb, largest_lead, lead_changes, times_tied)
                    VALUES (:team_id, :game_id, :points, :rebounds, :assists, :turnovers, :fgm, :fga, :fg3m, :fg3a,
                            :ftm, :fta, :plus_minus, :pts_paint, :pts_2nd_chance, :pts_fb, :largest_lead, :lead_changes, :times_tied)
                    ON CONFLICT DO NOTHING
                """),
                rows_to_insert
            )
            db.commit()
            total += len(rows_to_insert)
            print(f"  {total} team box scores inserted...")

    print(f"Team box scores total: {total}")
    db.close()


if __name__ == "__main__":
    print("Starting CSV load...")
    load_games()
    load_players()
    load_player_box_scores()
    load_team_box_scores()
    print("\nDone.")
