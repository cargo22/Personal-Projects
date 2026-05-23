import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# defining a chunk size to reduce processing power for large files
CHUNK_SIZE = 10000

# skipping games we don't necessarily care about
SKIP_GAME_TYPES = {"Preseason", "All-Star Game"}

# in-season tournament championship games — don't count toward regular season
# group stage games are duplicated as "Regular Season" in the CSV so they load correctly
CUP_GAME_TYPES = {"NBA Cup", "Emirates NBA Cup", "NBA Emirates Cup"}

# helper function to get season depending on date
def get_season(date):
    year = date.year if date.month >= 10 else date.year - 1
    return f"{year}-{str(year + 1)[2:]}"


# making sure game id's are forced to be 10 characters long
def pad_game_id(game_id):
    return str(int(game_id)).zfill(10)
