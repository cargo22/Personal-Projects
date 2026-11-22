import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from sqlalchemy import text
from db_connection import engine
from ml.build_features import get_rolling_average, get_home_away, get_opponent_defensive_rating, get_days_rest

def get_training_rows(start_season="2015-16", end_season="2025-26"):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT
                pbs.player_id,
                pbs.team_id,
                pbs.game_id,
                g.date,
                g.season,
                pbs.points
            FROM player_box_scores pbs
            JOIN games g on g.id = pbs.game_id
            WHERE g.season BETWEEN :start_season AND :end_season
                AND g.is_playoffs = False
        """), {"start_season": start_season, "end_season": end_season}).fetchall()
    return rows

def build_training_dataset(start_season="2015-16", end_season="2025-26", limit=None):
    rows = get_training_rows(start_season, end_season)
    if limit is not None:
        rows = rows[:limit]

    training_data = []

    with engine.connect() as conn:
        for player_id, team_id, game_id, date, season, points in rows:
            rolling_avg = get_rolling_average(conn, player_id, before_date=date)
            home_away = get_home_away(conn, team_id, game_id)
            opp_def_rating = get_opponent_defensive_rating(conn, team_id, game_id, before_date=date)
            rest = get_days_rest(conn, player_id, before_date=date)
            rolling_minutes = get_rolling_average(conn, player_id, before_date=date, stat_column="minutes_played")

            if rolling_avg is None:
                continue

            training_data.append({
                "rolling_avg": rolling_avg,
                "home_away": home_away,
                "opp_def_rating": opp_def_rating,
                "days_rest": rest,
                "season": season,
                "points": points,
                "rolling_minutes": rolling_minutes,
            })
    
    return pd.DataFrame(training_data)


if __name__ == "__main__":
    # training split: 2015-16 through 2021-22 — see project design notes for
    # why (validate on 2022-23, test on 2023-24/24-25/25-26, run separately later)
    print("Building training dataset (2015-16 through 2021-22)...")
    df = build_training_dataset(start_season="2015-16", end_season="2021-22", limit=500)
    out_path = os.path.join(os.path.dirname(__file__), "training_data.csv")
    df.to_csv(out_path, index=False)
    print(f"Done. {len(df)} rows saved to {out_path}")