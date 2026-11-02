import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from sqlalchemy import text
from db_connection import engine


def get_rolling_average(player_id, before_date, stat_column="points", window=5):
    with engine.connect() as conn:
        conn.execute(text(f"""
            SELECT AVG(sub.{stat_column}) AS rolling_avg
            FROM (
                SELECT pbs.{stat_column}
                FROM player_box_scores pbs
                JOIN games g ON g.id = pbs.game_id
                WHERE pbs.player_id = :player_id
                    AND g.date < :before_date
                ORDER BY g.date DESC
                LIMIT :window
            ) AS sub
            
        """))