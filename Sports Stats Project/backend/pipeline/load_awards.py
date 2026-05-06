import sys
import os
# expanding scope of current directory to find files
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from db_connection import SessionLocal, engine
import db_tables
from pipeline.utils import DATA_DIR

# function that takes the awards csv and loads it to the database
def load_awards():
    print("\n--- Loading Awards ---")
    # creating a live connection to PostgreSQL
    db = SessionLocal()

    # creating the tables defined in db_tables
    db_tables.Base.metadata.create_all(bind=engine)

    # wipes existing award rows before reloading
    db.query(db_tables.Award).delete()
    db.commit()

    # using pandas to read the player awards csv
    df = pd.read_csv(os.path.join(DATA_DIR, "Player Award Shares.csv"), encoding="latin-1")

    # counting how many entries we've seeded
    seeded = 0

    # looping through every row
    for _, row in df.iterrows():
        # skips rows where season or player name is missing
        if pd.isna(row.get("season")) or pd.isna(row.get("player")):
            continue

        # converting year won to associated season
        # aka 2006 -> 2005-06
        season_year = int(row["season"])
        season = f"{season_year - 1}-{str(season_year)[2:]}"

        # adding the award to our PostgreSQL database
        db.add(db_tables.Award(
            season=season,
            award=str(row["award"]).strip().lower(),
            player_name=str(row["player"]).strip(),
            winner=bool(row["winner"]),
            share=float(row["share"]) if pd.notna(row.get("share")) else None,
        ))
        seeded += 1

    # finalizing changes
    db.commit()

    # we are done seeding
    print(f"Awards inserted: {seeded}")
    db.close()


if __name__ == "__main__":
    # call the function if the file is ran
    load_awards()
