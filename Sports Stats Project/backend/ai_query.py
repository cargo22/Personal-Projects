# ai_query.py — takes a plain English question, asks Claude to write SQL, runs it, returns results

import os
import time
from sqlalchemy import create_engine, text
import anthropic
from dotenv import load_dotenv

# loads variables from .env into memory so os.getenv() can access them
load_dotenv()

# direct database connection for running raw SQL — bypasses the ORM because
# Claude generates dynamic queries that SQLAlchemy can't predict in advance
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# connects to the Claude API using the key from .env
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# the system prompt — tells Claude what our database looks like and how to write SQL for it
# cached with ephemeral so Anthropic stores it temporarily, reducing cost on repeated requests
SCHEMA_CONTEXT = """You are an expert NBA Data Analyst. You have a PostgreSQL database with these tables:

- teams (id, name, abbreviation, nickname, city, conference, division)
- players (id, name, position, is_active, team_id, draft_year, draft_round, draft_number) — draft columns are NULL for undrafted players
- games (id, date, season, home_team_id, away_team_id, home_score, away_score, is_playoffs)
- player_box_scores (id, player_id, game_id, team_id, points, rebounds, assists, steals, blocks, turnovers, minutes_played, fgm, fga, fg3m, fg3a, ftm, fta, plus_minus, true_shooting_pct, effective_fg_pct, usage_rate, offensive_rating, defensive_rating, net_rating, assist_pct, rebound_pct, player_impact_estimate, double_double, triple_double)
- team_box_scores (id, team_id, game_id, points, assists, rebounds, turnovers, fgm, fga, fg3m, fg3a, ftm, fta, offensive_rating, defensive_rating, pace)
- awards (id, season, award, player_name, winner, share) — award values: 'nba mvp', 'nba roy', 'nba dpoy', 'nba smoy', 'nba mip'. winner=true means they won. Use player_name directly, no join needed.

Rules:
- Return ONLY the SQL query. No explanations, no markdown, no code blocks.
- Always join player_box_scores with players on player_id to get player names.
- Always join team_box_scores with teams on team_id to get team names.
- Always join with games when filtering by season or date.
- Season format is like '2023-24'. Only use this format — never use numeric season IDs like '22015' or '12015'.
- The current season is '2025-26'. When the user says "this season", "current season", or "this year", use '2025-26'.
- Always filter to regular season only by default: WHERE g.season LIKE '____-__' AND g.is_playoffs = false. This applies to career stats too — "career" means regular season only unless the user says "including playoffs" or "postseason".
- Limit results to 10 rows unless the question asks for all or a specific number.
- For per-game averages, use AVG() on the relevant column in player_box_scores or team_box_scores.
- For team scoring averages, use AVG(team_box_scores.points) grouped by team.
- For player averages, use AVG() on player_box_scores columns grouped by player.
- When asked about wins/losses, calculate from games table: count games where home_score > away_score for home wins.
- To find a championship winner for a season, find the last playoff game of that season (MAX(date) WHERE is_playoffs = true AND season = '...') and determine who won it (home_score > away_score means home team won).
- To count championships for a team across all seasons, use a subquery or CTE that finds the winner of the last playoff game for each season, then count how many times that team appears.
- Always round floating point results to 2 decimal places using ROUND(value::numeric, 2)."""

# the output is list[dict] as the flow is:
# PostgreSQL row -> Python dict -> JSON -> React
def run_oracle_query(user_question: str) -> list[dict]:
    # expects a string (the user's question), returns a list of dictionaries (the results)

    # step 1 — send the question to Claude with the schema context
    # retries up to 3 times with a short wait between attempts to handle API timeouts
    last_error = None
    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                system=[
                    {
                        "type": "text",
                        "text": SCHEMA_CONTEXT,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {"role": "user", "content": user_question}
                ]
            )
            break
        except (anthropic.APITimeoutError, anthropic.APIConnectionError) as e:
            last_error = e
            if attempt < 2:
                time.sleep(2)
        except Exception:
            raise
    else:
        raise last_error

    # step 2 — extract the SQL string from Claude's response
    # response.content is a list of blocks — [0] grabs the first one, .text gets the string, .strip() removes whitespace
    sql = response.content[0].text.strip()
    if sql.startswith("```"):
        sql = sql.split("\n", 1)[1]
    if sql.endswith("```"):
        sql = sql.rsplit("```", 1)[0]
    sql = sql.strip()

    # step 3 — run the SQL on PostgreSQL
    # "with" ensures the connection is always closed when done, even if something crashes
    with engine.connect() as conn:
        result = conn.execute(text(sql))  # text() wraps the raw string so SQLAlchemy can execute it safely
        columns = result.keys()           # column names e.g. ["name", "points", "assists"]
        rows = result.fetchall()          # every row returned by the query

        # zip() pairs each column name with its value for every row
        # dict() turns those pairs into a dictionary e.g. {"name": "LeBron", "points": 30}
        # the list comprehension does this for every row, building the final list
        return [dict(zip(columns, row)) for row in rows]

# writing a function that will turn SQL result back into regular english
def summarize_results(user_question: str, results: list[dict]) -> str:
    last_error = None
    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=150,
                messages=[
                    {
                        "role": "user",
                        "content": f"Question: {user_question}\nData: {results}\n\nThe data above is the complete answer. Write one clear, natural sentence summarizing all the results. Do not say the data 'only contains' anything. No markdown, no extra explanation."
                    }
                ]
            )
            return response.content[0].text.strip()
        except (anthropic.APITimeoutError, anthropic.APIConnectionError) as e:
            last_error = e
            if attempt < 2:
                time.sleep(2)
        except Exception:
            raise
    raise last_error
                    
