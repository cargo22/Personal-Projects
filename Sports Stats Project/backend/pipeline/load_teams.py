import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from db_connection import SessionLocal
import db_tables
from pipeline.utils import DATA_DIR

# conference / division / state for the 30 current NBA teams, keyed by nba_team_id.
# these three fields do NOT exist in any Kaggle file — but they are static facts that
# rarely change. keeping them here (committed to the repo) is what makes the teams table
# fully reproducible on any machine: Kaggle CSVs give us everything else, this dict fills
# the rest, so load_all.py can rebuild the entire database from scratch anywhere.
TEAM_METADATA = {
    # Eastern Conference
    1610612737: ("East", "Southeast", "Georgia"),              # Atlanta Hawks
    1610612738: ("East", "Atlantic",  "Massachusetts"),        # Boston Celtics
    1610612739: ("East", "Central",   "Ohio"),                 # Cleveland Cavaliers
    1610612741: ("East", "Central",   "Illinois"),             # Chicago Bulls
    1610612748: ("East", "Southeast", "Florida"),              # Miami Heat
    1610612749: ("East", "Central",   "Wisconsin"),            # Milwaukee Bucks
    1610612751: ("East", "Atlantic",  "New York"),             # Brooklyn Nets
    1610612752: ("East", "Atlantic",  "New York"),             # New York Knicks
    1610612753: ("East", "Southeast", "Florida"),              # Orlando Magic
    1610612754: ("East", "Central",   "Indiana"),              # Indiana Pacers
    1610612755: ("East", "Atlantic",  "Pennsylvania"),         # Philadelphia 76ers
    1610612761: ("East", "Atlantic",  "Ontario"),              # Toronto Raptors
    1610612764: ("East", "Southeast", "District of Columbia"), # Washington Wizards
    1610612765: ("East", "Central",   "Michigan"),             # Detroit Pistons
    1610612766: ("East", "Southeast", "North Carolina"),       # Charlotte Hornets
    # Western Conference
    1610612740: ("West", "Southwest", "Louisiana"),            # New Orleans Pelicans
    1610612742: ("West", "Southwest", "Texas"),                # Dallas Mavericks
    1610612743: ("West", "Northwest", "Colorado"),             # Denver Nuggets
    1610612744: ("West", "Pacific",   "California"),           # Golden State Warriors
    1610612745: ("West", "Southwest", "Texas"),                # Houston Rockets
    1610612746: ("West", "Pacific",   "California"),           # Los Angeles Clippers
    1610612747: ("West", "Pacific",   "California"),           # Los Angeles Lakers
    1610612750: ("West", "Northwest", "Minnesota"),            # Minnesota Timberwolves
    1610612756: ("West", "Pacific",   "Arizona"),              # Phoenix Suns
    1610612757: ("West", "Northwest", "Oregon"),               # Portland Trail Blazers
    1610612758: ("West", "Pacific",   "California"),           # Sacramento Kings
    1610612759: ("West", "Southwest", "Texas"),                # San Antonio Spurs
    1610612760: ("West", "Northwest", "Oklahoma"),             # Oklahoma City Thunder
    1610612762: ("West", "Northwest", "Utah"),                 # Utah Jazz
    1610612763: ("West", "Southwest", "Tennessee"),            # Memphis Grizzlies
}


# function to load the 30 current NBA teams into the database
def load_teams():
    print("\n--- Loading Teams ---")
    # creating a live connection to PostgreSQL
    db = SessionLocal()

    # reading the history of every franchise the dataset has ever tracked
    df = pd.read_csv(os.path.join(DATA_DIR, "TeamHistories.csv"))

    # narrowing down to just the 30 current NBA franchises:
    # - seasonActiveTill == 2100 marks a team that is still active
    # - league == 'NBA' drops international and All-Star teams
    # - the 1610612xxx id format is the NBA's real team id (filters out the 9xxx placeholders)
    df = df[
        (df["seasonActiveTill"] == 2100)
        & (df["league"] == "NBA")
        & (df["teamId"] > 1000000000)
    ]

    seeded = 0
    # iterating through each current team
    for _, row in df.iterrows():
        nba_team_id = int(row["teamId"])

        # pulling the three fields the csv can't give us from our committed dict
        conference, division, state = TEAM_METADATA.get(nba_team_id, (None, None, None))

        # building the display fields from the csv (e.g. "Los Angeles" + "Lakers")
        city = str(row["teamCity"]).strip()
        nickname = str(row["teamName"]).strip()
        full_name = f"{city} {nickname}"
        abbreviation = str(row["teamAbbrev"]).strip()
        year_founded = int(row["seasonFounded"]) if pd.notna(row.get("seasonFounded")) else None

        # check if the team already exists so re-running the loader never duplicates rows
        existing = db.query(db_tables.Team).filter(
            db_tables.Team.nba_team_id == nba_team_id
        ).first()

        # if it exists, just refresh its values (keeps both machines identical)
        if existing:
            existing.name = full_name
            existing.abbreviation = abbreviation
            existing.nickname = nickname
            existing.city = city
            existing.state = state
            existing.conference = conference
            existing.division = division
            existing.year_founded = year_founded
            continue

        # otherwise add a brand new team
        db.add(db_tables.Team(
            nba_team_id=nba_team_id,
            name=full_name,
            abbreviation=abbreviation,
            nickname=nickname,
            city=city,
            state=state,
            conference=conference,
            division=division,
            year_founded=year_founded,
        ))
        seeded += 1

    # save changes
    db.commit()
    print(f"Teams inserted: {seeded}")
    db.close()


if __name__ == "__main__":
    # run function when file is executed
    load_teams()
