import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from sqlalchemy import text
from db_connection import engine
from ml.build_features import get_rolling_average, get_home_away, get_opponent_defensive_rating, get_days_rest

def get_training_rows():
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
        """), {"start_season": "2015-16", "end_season": "2025-26"}).fetchall()
    return rows