# establishes and defines FastAPI behavior

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
import db_tables
from db_connection import engine
from ai_query import run_oracle_query, summarize_results

# creates all database tables on startup if they don't already exist
db_tables.Base.metadata.create_all(bind=engine)

# the FastAPI app — everything attaches to this object
app = FastAPI(title="Sports Oracle API")

# allows the React frontend (localhost:5173) to make requests to this backend
# without this, the browser would block all requests due to CORS security rules
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# defines what a valid /ask request must look like — Pydantic rejects anything that doesn't match
class AskRequest(BaseModel):
    question: str
    mode: str = "past"

# health check — confirms the server is running
@app.get("/")
def read_root():
    return {"message": "The engine is live!"}

# main endpoint — receives a question, runs the oracle, returns results
@app.post("/ask")
def ask(request: AskRequest):
    try:
        results = run_oracle_query(request.question, request.mode)
        summarized_result = summarize_results(request.question, results)
        return {"question": request.question, "summary": summarized_result, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# stat column lookup — controls what goes into the SQL query
STAT_COLS = {"ppg": "points", "rpg": "rebounds", "apg": "assists"}

# returns current season leaders for regular season and playoffs
@app.get("/api/leaders")
def get_leaders():
    try:
        with engine.connect() as conn:
            def fetch(is_playoffs, stat_key, min_games):
                col = STAT_COLS[stat_key]
                rows = conn.execute(text(f"""
                    SELECT p.name, ROUND(AVG(pbs.{col})::numeric, 1) AS value, COUNT(*) AS gp
                    FROM player_box_scores pbs
                    JOIN players p ON p.id = pbs.player_id
                    JOIN games g ON g.id = pbs.game_id
                    WHERE g.season = '2025-26' AND g.is_playoffs = :playoffs AND pbs.{col} IS NOT NULL
                    GROUP BY p.name
                    HAVING COUNT(*) >= :min_games
                    ORDER BY value DESC
                    LIMIT 5
                """), {"playoffs": is_playoffs, "min_games": min_games}).fetchall()
                return [{"name": r[0], "value": float(r[1]), "gp": r[2]} for r in rows]

            return {
                "regular": {
                    "ppg": fetch(False, "ppg", 20),
                    "rpg": fetch(False, "rpg", 20),
                    "apg": fetch(False, "apg", 20),
                },
                "playoffs": {
                    "ppg": fetch(True, "ppg", 5),
                    "rpg": fetch(True, "rpg", 5),
                    "apg": fetch(True, "apg", 5),
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
