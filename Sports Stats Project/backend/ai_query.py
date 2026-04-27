# ai_query.py — takes a plain English question, asks Claude to write SQL, runs it, returns results

import os
# text is a SQLAlchemy wrapper that lets you safely run a raw SQL string
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
- players (id, name, position, is_active, team_id)
- games (id, date, season, home_team_id, away_team_id, home_score, away_score, is_playoffs)
- player_box_scores (id, player_id, game_id, team_id, points, rebounds, assists, steals, blocks, turnovers, minutes_played, fgm, fga, fg3m, fg3a, ftm, fta, plus_minus)
- team_box_scores (id, team_id, game_id, points, assists, rebounds, turnovers, fgm, fga, fg3m, fg3a, ftm, fta, offensive_rating, defensive_rating, pace)

Rules:
- Return ONLY the SQL query. No explanations, no markdown, no code blocks.
- Always join player_box_scores with players on player_id to get player names.
- Always join with games when filtering by season or date.
- Season format is like '2023-24'.
- Limit results to 10 rows unless the question asks for all or a specific number."""

# the output is list[dict] as the flow is:
# PostgreSQL row -> Python dict -> JSON -> React
def run_oracle_query(user_question: str) -> list[dict]:
    # expects a string (the user's question), returns a list of dictionaries (the results)

    # step 1 — send the question to Claude with the schema context
    # Claude reads the schema and returns a raw SQL query as plain text
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # fastest and cheapest Claude model, plenty for SQL generation
        max_tokens=500,                      # SQL queries are short, 500 tokens is more than enough
        system=[
            {
                "type": "text",
                "text": SCHEMA_CONTEXT,
                "cache_control": {"type": "ephemeral"}  # Anthropic caches this to reduce cost per request
            }
        ],
        messages=[
            {"role": "user", "content": user_question}  # the question typed by the user
        ]
    )

    # step 2 — extract the SQL string from Claude's response
    # response.content is a list of blocks — [0] grabs the first one, .text gets the string, .strip() removes whitespace
    sql = response.content[0].text.strip()

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
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[
            {
                "role": "user",
                "content": f"Question: {user_question}\nData: {results}\n\nWrite in one clear, natural sentence that answers the question using the data. No markdown, no extra explanation."
            }
        ]
    )
    return response.content[0].text.strip()
                      
# quick test — only runs if you execute this file directly with: python ask_oracle.py
if __name__ == "__main__":
    q = "Who scored the most points in a single game in the 2023-24 season?"
    results = run_oracle_query(q)
    for row in results:
        print(row)
