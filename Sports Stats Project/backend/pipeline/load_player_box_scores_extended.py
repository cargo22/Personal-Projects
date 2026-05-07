import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from sqlalchemy import text
from db_connection import SessionLocal, engine
import db_tables
from pipeline.utils import DATA_DIR, CHUNK_SIZE, pad_game_id

# covers games since 1996 when NBA.com started tracking advanced stats
# runs as a second pass after load_player_box_scores.py to fill in advanced columns


def load_player_box_scores_extended():
    print("\n--- Loading Player Box Scores (Extended) ---")
    db = SessionLocal()

    print("  Building lookup caches...")
    game_map = {g.nba_game_id: g.id for g in db.query(db_tables.Game).all()}
    player_map = {p.nba_player_id: p.id for p in db.query(db_tables.Player).all()}

    total = 0
    for chunk in pd.read_csv(os.path.join(DATA_DIR, "PlayerStatisticsExtended.csv"), chunksize=CHUNK_SIZE, low_memory=False):
        rows_to_update = []

        for _, row in chunk.iterrows():
            if pd.isna(row.get("personId")) or pd.isna(row.get("gameId")):
                continue

            nba_game_id = pad_game_id(row["gameId"])
            game_id = game_map.get(nba_game_id)
            player_id = player_map.get(int(row["personId"]))

            if not game_id or not player_id:
                continue

            rows_to_update.append({
                "player_id": player_id,
                "game_id": game_id,
                "true_shooting_pct": float(row["trueShootingPercentage"]) if pd.notna(row.get("trueShootingPercentage")) else None,
                "effective_fg_pct": float(row["effectiveFieldGoalPercentage"]) if pd.notna(row.get("effectiveFieldGoalPercentage")) else None,
                "usage_rate": float(row["usagePercentage"]) if pd.notna(row.get("usagePercentage")) else None,
                "offensive_rating": float(row["offensiveRating"]) if pd.notna(row.get("offensiveRating")) else None,
                "defensive_rating": float(row["defensiveRating"]) if pd.notna(row.get("defensiveRating")) else None,
                "net_rating": float(row["netRating"]) if pd.notna(row.get("netRating")) else None,
                "assist_pct": float(row["assistPercentage"]) if pd.notna(row.get("assistPercentage")) else None,
                "rebound_pct": float(row["reboundPercentage"]) if pd.notna(row.get("reboundPercentage")) else None,
                "player_impact_estimate": float(row["playerImpactEstimate"]) if pd.notna(row.get("playerImpactEstimate")) else None,
                "double_double": bool(row["doubleDouble"]) if pd.notna(row.get("doubleDouble")) else None,
                "triple_double": bool(row["tripleDouble"]) if pd.notna(row.get("tripleDouble")) else None,
            })

        if rows_to_update:
            db.execute(
                text("""
                    UPDATE player_box_scores SET
                        true_shooting_pct = :true_shooting_pct,
                        effective_fg_pct = :effective_fg_pct,
                        usage_rate = :usage_rate,
                        offensive_rating = :offensive_rating,
                        defensive_rating = :defensive_rating,
                        net_rating = :net_rating,
                        assist_pct = :assist_pct,
                        rebound_pct = :rebound_pct,
                        player_impact_estimate = :player_impact_estimate,
                        double_double = :double_double,
                        triple_double = :triple_double
                    WHERE player_id = :player_id AND game_id = :game_id
                """),
                rows_to_update
            )
            db.commit()
            total += len(rows_to_update)
            print(f"  {total} player box scores updated...")

    print(f"Player box scores extended total: {total}")
    db.close()


if __name__ == "__main__":
    load_player_box_scores_extended()
