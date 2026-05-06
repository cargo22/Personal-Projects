import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from db_connection import SessionLocal
import db_tables
from pipeline.utils import DATA_DIR

# function to load players to the database
def load_players():
    print("\n--- Loading Players ---")
    # creating live connection to PostgreSQL
    db = SessionLocal()

    # reading the csv of all players in NBA's history
    df = pd.read_csv(os.path.join(DATA_DIR, "Players.csv"))

    seeded = 0

    # iterating through each row (player)
    for _, row in df.iterrows():
        position = None

        # extracting player's position
        if row.get("guard") == 1:
            position = "G"
        elif row.get("forward") == 1:
            position = "F"
        elif row.get("center") == 1:
            position = "C"

        # determining retire year or if player is active
        to_year = int(row["toYear"]) if pd.notna(row.get("toYear")) else None
        is_active = to_year is not None and to_year >= 2024

        # making sure the player has a valid id
        existing = db.query(db_tables.Player).filter(
            db_tables.Player.nba_player_id == int(row["personId"])
        ).first()

        # case for if the player already exists in the database. just update the values
        if existing:
            existing.draft_year = int(row["draftYear"]) if pd.notna(row.get("draftYear")) else existing.draft_year
            existing.draft_round = int(row["draftRound"]) if pd.notna(row.get("draftRound")) else existing.draft_round
            existing.draft_number = int(row["draftNumber"]) if pd.notna(row.get("draftNumber")) else existing.draft_number
            existing.position = position or existing.position
            existing.is_active = is_active
            continue

        # adding a bran new player to the database and assigning their values
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

    # save changes
    db.commit()
    print(f"Players inserted: {seeded}")
    db.close()


if __name__ == "__main__":
    # call function when file is executrd
    load_players()
