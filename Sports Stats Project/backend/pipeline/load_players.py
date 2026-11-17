import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from db_connection import SessionLocal
import db_tables
from pipeline.utils import DATA_DIR

# some names in Players.csv belong to TWO (or more) different real people — most often
# father/son pairs (e.g. Mike Dunleavy Sr./Jr.) — not duplicate records of the same person.
# "has real draft info" can't tell these apart (both are real draft picks), so instead we
# check whether their actual playing careers overlap in time: same person's duplicate
# records happen in the same era (overlapping dates), while two different people's careers
# don't overlap (a multi-year gap between one retiring and the other debuting).
def deduplicate_players(df):
    df = df.copy()
    df["full_name"] = df["firstName"].astype(str).str.strip() + " " + df["lastName"].astype(str).str.strip()
    df["has_draft_info"] = df["draftYear"].notna()

    # each personId's real game-date range, straight from the raw box score CSV —
    # games/player_box_scores aren't loaded into the database yet at this point in the
    # pipeline, so we can't query them; the source CSV is the only data available here
    stats = pd.read_csv(os.path.join(DATA_DIR, "PlayerStatistics.csv"), usecols=["personId", "gameDate"])
    stats["gameDate"] = pd.to_datetime(stats["gameDate"])
    date_ranges = stats.groupby("personId")["gameDate"].agg(["min", "max"])

    rows_to_keep = []
    for _, group in df.groupby("full_name"):
        if len(group) == 1:
            rows_to_keep.append(group)
            continue

        # only candidates with recorded games can be compared for a date gap — anyone
        # who never played has nothing to compare, and contributes no evidence either way
        ranges = []
        for _, candidate in group.iterrows():
            pid = candidate["personId"]
            if pid in date_ranges.index:
                ranges.append((pid, date_ranges.loc[pid, "min"], date_ranges.loc[pid, "max"]))

        ranges.sort(key=lambda r: r[1])
        is_different_people = any(
            (ranges[i + 1][1] - ranges[i][2]).days > 365 * 3
            for i in range(len(ranges) - 1)
        )

        if is_different_people:
            # genuinely different real people sharing a name — keep every one of them
            rows_to_keep.append(group)
        else:
            # same real person (or no game data to compare at all) — keep just one record
            best = group.sort_values("has_draft_info", ascending=False).iloc[[0]]
            rows_to_keep.append(best)

    return pd.concat(rows_to_keep, ignore_index=True)

# function to load players to the database
def load_players():
    print("\n--- Loading Players ---")
    # creating live connection to PostgreSQL
    db = SessionLocal()

    # reading the csv of all players in NBA's history
    df = pd.read_csv(os.path.join(DATA_DIR, "Players.csv"))
    df = deduplicate_players(df)

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
