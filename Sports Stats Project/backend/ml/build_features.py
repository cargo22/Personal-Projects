import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from sqlalchemy import text
from db_connection import engine


def get_rolling_average(player_id, before_date, stat_column="points", window=5):
    with engine.connect() as conn:
        return conn.execute(text(f"""
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
            
        """), {"player_id": player_id, "before_date": before_date, "window": window}).scalar()

def get_home_away(team_id, game_id):
    with engine.connect() as conn:
        home_team_id = conn.execute(text(f"""
            SELECT home_team_id
            FROM games
            WHERE id = :game_id
        """), {"game_id": game_id}).scalar()

        if home_team_id == team_id:
            return 1
        else:
            return 0

def get_days_rest(player_id, before_date):
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT CAST(:before_date AS date) - g.date AS days_rest
            FROM player_box_scores pbs
            JOIN games g ON g.id = pbs.game_id
            WHERE pbs.player_id = :player_id
            AND g.date < :before_date
            ORDER BY g.date DESC
            LIMIT 1
        """), {"player_id": player_id, "before_date": before_date}).scalar()

def get_opponent_team_id(team_id, game_id):
    home_team = get_home_away(team_id, game_id)
    if home_team == 1:
        with engine.connect() as conn:
            return conn.execute(text("""
                SELECT away_team_id
                FROM games
                WHERE id = :game_id
            """), {"game_id": game_id}).scalar()
    else:
        with engine.connect() as conn:
            return conn.execute(text("""
                SELECT home_team_id
                FROM games
                WHERE id = :game_id
            """), {"game_id": game_id}).scalar()

def get_opponent_defensive_rating(team_id, game_id, before_date, window=10):
    opponent_id = get_opponent_team_id(team_id, game_id)

    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT AVG(sub.defensive_rating) AS rolling_avg
            FROM (
                SELECT tbs.defensive_rating
                FROM team_box_scores tbs
                JOIN games g ON g.id = tbs.game_id
                WHERE tbs.team_id = :opponent_id
                    AND g.date < :before_date
                ORDER BY g.date DESC
                LIMIT :window
            ) AS sub
        """), {"opponent_id": opponent_id, "before_date": before_date, "window": window}).scalar()