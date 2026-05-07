import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from sqlalchemy import text
from db_connection import SessionLocal
import db_tables
from pipeline.utils import DATA_DIR, CHUNK_SIZE, pad_game_id

# covers games since 1996 when NBA.com started tracking advanced stats
# runs as a second pass after load_team_box_scores.py to fill in offensive_rating, defensive_rating, and pace


def load_team_box_scores_extended():
    print("\n--- Loading Team Box Scores (Extended) ---")
    db = SessionLocal()

    print("  Building lookup caches...")
    game_map = {g.nba_game_id: g.id for g in db.query(db_tables.Game).all()}
    team_map = {t.nba_team_id: t.id for t in db.query(db_tables.Team).all()}

    total = 0
    for chunk in pd.read_csv(os.path.join(DATA_DIR, "TeamStatisticsExtended.csv"), chunksize=CHUNK_SIZE, low_memory=False):
        rows_to_update = []

        for _, row in chunk.iterrows():
            if pd.isna(row.get("gameId")) or pd.isna(row.get("teamId")):
                continue

            nba_game_id = pad_game_id(row["gameId"])
            game_id = game_map.get(nba_game_id)
            team_id = team_map.get(int(row["teamId"]))

            if not game_id or not team_id:
                continue

            rows_to_update.append({
                "team_id": team_id,
                "game_id": game_id,
                "offensive_rating": float(row["offensiveRating"]) if pd.notna(row.get("offensiveRating")) else None,
                "defensive_rating": float(row["defensiveRating"]) if pd.notna(row.get("defensiveRating")) else None,
                "pace": float(row["pace"]) if pd.notna(row.get("pace")) else None,
            })

        if rows_to_update:
            db.execute(
                text("""
                    UPDATE team_box_scores SET
                        offensive_rating = :offensive_rating,
                        defensive_rating = :defensive_rating,
                        pace = :pace
                    WHERE team_id = :team_id AND game_id = :game_id
                """),
                rows_to_update
            )
            db.commit()
            total += len(rows_to_update)
            print(f"  {total} team box scores updated...")

    print(f"Team box scores extended total: {total}")
    db.close()


if __name__ == "__main__":
    load_team_box_scores_extended()
