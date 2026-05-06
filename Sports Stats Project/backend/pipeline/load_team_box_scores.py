import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from sqlalchemy import text
from db_connection import SessionLocal
import db_tables
from pipeline.utils import DATA_DIR, CHUNK_SIZE, pad_game_id

# function to load a team's box score
def load_team_box_scores():
    print("\n--- Loading Team Box Scores ---")
    # creating a live connection to PostgreSQL
    db = SessionLocal()

    print("  Building lookup caches...")

    # connecting NBA game id to internal ID as well as the team
    game_map = {g.nba_game_id: g.id for g in db.query(db_tables.Game).all()}
    team_map = {t.nba_team_id: t.id for t in db.query(db_tables.Team).all()}

    total = 0
    # read csv in chunks
    for chunk in pd.read_csv(os.path.join(DATA_DIR, "TeamStatistics.csv"), chunksize=CHUNK_SIZE, low_memory=False):
        rows_to_insert = []

        # for each row in the chunk
        for _, row in chunk.iterrows():
            # extract necessary id's
            nba_game_id = pad_game_id(row["gameId"])
            game_id = game_map.get(nba_game_id)
            team_id = team_map.get(int(row["teamId"])) if pd.notna(row.get("teamId")) else None

            # if id's are not valid, continue
            if not game_id or not team_id:
                continue

            # inserting the game and necessary values associated with each game
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

        # add to db only if there are actually any rows to insert for this chunk
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

            # save changes
            db.commit()
            total += len(rows_to_insert)
            print(f"  {total} team box scores inserted...")

    print(f"Team box scores total: {total}")
    db.close()


if __name__ == "__main__":
    # call function when file is executed
    load_team_box_scores()
