# load_initial_data.py — one-time script that loads the Kaggle SQLite dataset into PostgreSQL
# run this once to populate teams, players, games, and team box scores
# player box scores are handled separately by fetch_player_box_scores.py
# we only run this once, but will keep it to remind us of what exactly was ported to PostgreSQL

# nba_api gives us a live list of active players to patch any gaps the Kaggle data has
from nba_api.stats.static import players as static_players

# text() wraps raw SQL strings so SQLAlchemy can execute them safely
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# our PostgreSQL connection and engine from db_connection.py
from backend.db_connection import SessionLocal, engine

# our table definitions
import backend.db_tables as db_tables

# creates PostgreSQL tables if they don't exist yet — safe to run even if tables already exist
db_tables.Base.metadata.create_all(bind=engine)

# opens a connection to the Kaggle SQLite file — this is the data source, not the destination
sqlite_engine = create_engine("sqlite:///data/nba.sqlite")
SqliteSession = sessionmaker(bind=sqlite_engine)


def seed_teams():
    sqlite_db = SqliteSession()  # session for reading from SQLite
    pg_db = SessionLocal()       # session for writing to PostgreSQL

    # reads every row from the 'team' table in the Kaggle SQLite file
    rows = sqlite_db.execute(text("SELECT * FROM team")).fetchall()
    seeded = 0

    for row in rows:
        # skip this team if it already exists in PostgreSQL — avoids duplicates
        existing = pg_db.query(db_tables.Team).filter(
            db_tables.Team.nba_team_id == int(row.id)
        ).first()

        if existing:
            continue

        # map the SQLite row to a Team object and add it to PostgreSQL
        team = db_tables.Team(
            nba_team_id = int(row.id),
            name = row.full_name,
            abbreviation = row.abbreviation,
            nickname = row.nickname,
            city = row.city,
            state = row.state,
            year_founded = int(row.year_founded) if row.year_founded else None,
        )

        pg_db.add(team)
        seeded += 1

    pg_db.commit()
    print(f"Teams seeded: {seeded}")
    sqlite_db.close()
    pg_db.close()


def seed_players():
    sqlite_db = SqliteSession()
    pg_db = SessionLocal()

    print("reading players from Kaggle dataset")
    # common_player_info has detailed player bios — height, weight, draft info, etc.
    rows = sqlite_db.execute(text("SELECT * FROM common_player_info")).fetchall()

    for row in rows:
        # skip if player already exists in PostgreSQL
        existing = pg_db.query(db_tables.Player).filter(
            db_tables.Player.nba_player_id == int(row.person_id)
        ).first()

        if not existing:
            # look up which team this player belongs to using their team_id
            team = None
            if row.team_id:
                team = pg_db.query(db_tables.Team).filter(
                    db_tables.Team.nba_team_id == int(row.team_id)
                ).first()

            # map the SQLite row to a Player object
            player = db_tables.Player(
                nba_player_id = int(row.person_id),
                name = row.display_first_last,
                first_name = row.first_name,
                last_name = row.last_name,
                position = row.position,
                height_inches = convert_height(row.height) if row.height else None,
                weight_lbs = int(row.weight) if row.weight else None,
                jersey_number = row.jersey,
                birthdate = parse_date(row.birthdate),
                country = row.country,
                school = row.school,
                # 'Undrafted' is a string in the dataset, not a number — treat it as None
                draft_year = int(row.draft_year) if row.draft_year and row.draft_year != 'Undrafted' else None,
                draft_round = int(row.draft_round) if row.draft_round and row.draft_round != 'Undrafted' else None,
                draft_number = int(row.draft_number) if row.draft_number and row.draft_number != 'Undrafted' else None,
                season_exp = int(row.season_exp) if row.season_exp else None,
                greatest_75_flag = row.greatest_75_flag == 'Y',  # stored as 'Y'/'N' in SQLite
                is_active = row.rosterstatus == "Active",
                team_id = team.id if team else None,
            )
            pg_db.add(player)

    # the Kaggle data may be outdated — patch with live active players from the NBA API
    print("syncing recent players")
    modern_players = static_players.get_active_players()

    for p in modern_players:
        existing = pg_db.query(db_tables.Player).filter(
            db_tables.Player.nba_player_id == p['id']
        ).first()

        if not existing:
            # add any active player not already in our database
            player = db_tables.Player(
                nba_player_id = p['id'],
                name = p['full_name'],
                first_name = p['first_name'],
                last_name = p['last_name'],
                is_active = True
            )
            pg_db.add(player)
        else:
            # mark existing players as active in case the Kaggle data had them wrong
            existing.is_active = True

    pg_db.commit()
    print(f"Player seeding and synchronization complete")
    sqlite_db.close()
    pg_db.close()


def seed_games():
    sqlite_db = SqliteSession()
    pg_db = SessionLocal()

    # the 'game' table in SQLite has one row per game with both home and away stats combined
    rows = sqlite_db.execute(text("SELECT * FROM game")).fetchall()

    seeded = 0
    for row in rows:
        # skip if this game already exists in PostgreSQL
        existing = pg_db.query(db_tables.Game).filter(
            db_tables.Game.nba_game_id == row.game_id
        ).first()
        if existing:
            continue

        # look up home and away teams by their NBA team ID
        home_team = pg_db.query(db_tables.Team).filter(
            db_tables.Team.nba_team_id == int(row.team_id_home)
        ).first()
        away_team = pg_db.query(db_tables.Team).filter(
            db_tables.Team.nba_team_id == int(row.team_id_away)
        ).first()

        # skip games where we can't find both teams
        if not home_team or not away_team:
            continue

        game = db_tables.Game(
            nba_game_id=row.game_id,
            date=parse_date(row.game_date),
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            home_score=int(row.pts_home) if row.pts_home else None,
            away_score=int(row.pts_away) if row.pts_away else None,
            season=row.season_id,
            is_playoffs=row.season_type == 'Playoffs' if hasattr(row, 'season_type') else False,
        )
        pg_db.add(game)
        seeded += 1

        # commit in batches of 1000 to avoid holding too much in memory at once
        if seeded % 1000 == 0:
            pg_db.commit()
            print(f"  {seeded} games seeded so far...")

    pg_db.commit()
    print(f"Games seeded: {seeded}")
    sqlite_db.close()
    pg_db.close()


def seed_team_box_scores():
    sqlite_db = SqliteSession()
    pg_db = SessionLocal()

    # same 'game' table — each row has both home and away team stats
    rows = sqlite_db.execute(text("SELECT * FROM game")).fetchall()

    seeded = 0
    for row in rows:
        # find the matching game we already inserted into PostgreSQL
        game = pg_db.query(db_tables.Game).filter(
            db_tables.Game.nba_game_id == row.game_id
        ).first()
        if not game:
            continue

        home_team = pg_db.query(db_tables.Team).filter(
            db_tables.Team.nba_team_id == int(row.team_id_home)
        ).first()
        away_team = pg_db.query(db_tables.Team).filter(
            db_tables.Team.nba_team_id == int(row.team_id_away)
        ).first()

        if not home_team or not away_team:
            continue

        # insert home team box score if it doesn't already exist
        home_exists = pg_db.query(db_tables.TeamBoxScore).filter(
            db_tables.TeamBoxScore.game_id == game.id,
            db_tables.TeamBoxScore.team_id == home_team.id
        ).first()

        if not home_exists:
            pg_db.add(db_tables.TeamBoxScore(
                team_id=home_team.id,
                game_id=game.id,
                fgm=int(row.fgm_home) if row.fgm_home else None,
                fga=int(row.fga_home) if row.fga_home else None,
                fg3m=int(row.fg3m_home) if row.fg3m_home else None,
                fg3a=int(row.fg3a_home) if row.fg3a_home else None,
                ftm=int(row.ftm_home) if row.ftm_home else None,
                fta=int(row.fta_home) if row.fta_home else None,
                rebounds=int(row.reb_home) if row.reb_home else None,
                assists=int(row.ast_home) if row.ast_home else None,
                turnovers=int(row.tov_home) if row.tov_home else None,
                points=int(row.pts_home) if row.pts_home else None,
                plus_minus=int(row.plus_minus_home) if row.plus_minus_home else None,
            ))
            seeded += 1

        # insert away team box score if it doesn't already exist
        away_exists = pg_db.query(db_tables.TeamBoxScore).filter(
            db_tables.TeamBoxScore.game_id == game.id,
            db_tables.TeamBoxScore.team_id == away_team.id
        ).first()

        if not away_exists:
            pg_db.add(db_tables.TeamBoxScore(
                team_id=away_team.id,
                game_id=game.id,
                fgm=int(row.fgm_away) if row.fgm_away else None,
                fga=int(row.fga_away) if row.fga_away else None,
                fg3m=int(row.fg3m_away) if row.fg3m_away else None,
                fg3a=int(row.fg3a_away) if row.fg3a_away else None,
                ftm=int(row.ftm_away) if row.ftm_away else None,
                fta=int(row.fta_away) if row.fta_away else None,
                rebounds=int(row.reb_away) if row.reb_away else None,
                assists=int(row.ast_away) if row.ast_away else None,
                turnovers=int(row.tov_away) if row.tov_away else None,
                points=int(row.pts_away) if row.pts_away else None,
                plus_minus=int(row.plus_minus_away) if row.plus_minus_away else None,
            ))
            seeded += 1

        # commit in batches of 1000 to avoid holding too much in memory
        if seeded % 1000 == 0 and seeded > 0:
            pg_db.commit()
            print(f"  {seeded} team box scores seeded so far...")

    pg_db.commit()
    print(f"Team box scores seeded: {seeded}")
    sqlite_db.close()
    pg_db.close()


def convert_height(height: str) -> int:
    # converts height from "6-9" format to total inches (81)
    try:
        feet, inches = height.split("-")
        return (int(feet) * 12) + int(inches)
    except:
        return None


def parse_date(date_str):
    # converts a date string like "2023-10-24" to a Python date object
    if not date_str:
        return None
    try:
        from datetime import datetime
        return datetime.strptime(str(date_str)[:10], "%Y-%m-%d").date()
    except:
        return None


# only runs if you execute this file directly: python load_initial_data.py
if __name__ == "__main__":
    print("Starting seed...")
    print("\n--- Step 1: Teams ---")
    seed_teams()
    print("\n--- Step 2: Players ---")
    seed_players()
    print("\n--- Step 3: Games ---")
    seed_games()
    print("\n--- Step 4: Team Box Scores ---")
    seed_team_box_scores()
    print("\nSeed complete. Player box scores will be populated separately via fetch_player_box_scores.py")
