import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from sqlalchemy import text
from db_connection import SessionLocal
import db_tables
from pipeline.utils import DATA_DIR, CHUNK_SIZE, pad_game_id

# function to load individual player box scores
def load_player_box_scores():
    print("\n--- Loading Player Box Scores ---")

    # creating a live connection to PostgreSQL
    db = SessionLocal()

    print("  Building lookup caches...")
    # creating maps to link NBA IDs to our internal database IDs
    game_map = {g.nba_game_id: g.id for g in db.query(db_tables.Game).all()}
    player_map = {p.nba_player_id: p.id for p in db.query(db_tables.Player).all()}
    team_map = {t.nba_team_id: t.id for t in db.query(db_tables.Team).all()}

    total = 0
    # read csv chunks at a time since the csv is EXTREMELY large
    for chunk in pd.read_csv(os.path.join(DATA_DIR, "PlayerStatistics.csv"), chunksize=CHUNK_SIZE, low_memory=False):
        rows_to_insert = []

        # iterating through every row in the current chunk
        for _, row in chunk.iterrows():
            # making sure that our data is valid
            if pd.isna(row.get("personId")) or pd.isna(row.get("gameId")):
                continue
            # making sure the player actually played that day
            if pd.isna(row.get("numMinutes")):
                continue

            raw_min = row["numMinutes"]
            # converting time played into number of minutes
            try:
                if ":" in str(raw_min):
                    parts = str(raw_min).split(":")
                    minutes_val = int(parts[0]) + int(parts[1]) / 60
                else:
                    minutes_val = float(raw_min)
            except (ValueError, IndexError):
                continue

            # if they played 0 minutes, don't add since it's likely a DNP
            if minutes_val == 0:
                continue

            # extracting necessary data 
            nba_game_id = pad_game_id(row["gameId"])
            game_id = game_map.get(nba_game_id)
            player_id = player_map.get(int(row["personId"]))
            team_id = team_map.get(int(row["playerteamId"])) if pd.notna(row.get("playerteamId")) else None

            # continuing only if data is valid
            if not game_id or not player_id:
                continue

            # inserting player box score
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

        # only insert if there is something to insert
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

            # save changes
            db.commit()
            total += len(rows_to_insert)
            print(f"  {total} player box scores inserted...")

    # we are done with all inserts
    print(f"Player box scores total: {total}")
    db.close()


if __name__ == "__main__":
    # run the function when the file is executed
    load_player_box_scores()
