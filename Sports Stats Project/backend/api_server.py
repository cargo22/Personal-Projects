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

# returns current season leaders for regular season and playoffs for 'present' mode
@app.get("/api/leaders")
def get_leaders():
    try:
        with engine.connect() as conn:
            # function that returns top 10 players, sorting by ppg and displaying ppg, rpg, and apg
            def fetch_players(is_playoffs, min_games):
                rows = conn.execute(text("""
                    SELECT
                        p.name,
                        ROUND(AVG(pbs.points)::numeric, 1)   AS ppg,
                        ROUND(AVG(pbs.rebounds)::numeric, 1) AS rpg,
                        ROUND(AVG(pbs.assists)::numeric, 1)  AS apg,
                        COUNT(*) AS gp
                    FROM player_box_scores pbs
                    JOIN players p ON p.id = pbs.player_id
                    JOIN games g   ON g.id = pbs.game_id
                    WHERE g.season = '2025-26' AND g.is_playoffs = :playoffs
                      AND g.nba_game_id NOT LIKE '0062%'
                    GROUP BY p.name
                    HAVING COUNT(*) >= :min_games
                    ORDER BY ppg DESC
                    LIMIT 10
                """), {"playoffs": is_playoffs, "min_games": min_games}).fetchall()
                return [{"name": r[0], "ppg": float(r[1]), "rpg": float(r[2]),
                         "apg": float(r[3]), "gp": r[4]} for r in rows]

            # new addition: we will also be displaying team 
            def fetch_team_record(is_playoffs):
                rows = conn.execute(text("""
                    SELECT
                        t.name,
                        COUNT(CASE WHEN (g.home_team_id = t.id AND g.home_score > g.away_score)
                                     OR (g.away_team_id = t.id AND g.away_score > g.home_score)
                                   THEN 1 END) AS wins,
                        COUNT(CASE WHEN (g.home_team_id = t.id AND g.home_score < g.away_score)
                                     OR (g.away_team_id = t.id AND g.away_score < g.home_score)
                                   THEN 1 END) AS losses,
                        ROUND(
                            COUNT(CASE WHEN (g.home_team_id = t.id AND g.home_score > g.away_score)
                                         OR (g.away_team_id = t.id AND g.away_score > g.home_score)
                                       THEN 1 END)::numeric / NULLIF(COUNT(*), 0), 3
                        ) AS win_pct
                    FROM teams t
                    JOIN games g ON (g.home_team_id = t.id OR g.away_team_id = t.id)
                    WHERE g.season = '2025-26' AND g.is_playoffs = :playoffs
                      AND g.home_score IS NOT NULL
                      AND g.nba_game_id NOT LIKE '0062%'
                    GROUP BY t.name
                    ORDER BY wins DESC
                    LIMIT 10
                """), {"playoffs": is_playoffs}).fetchall()
                return [{"name": r[0], "wins": r[1], "losses": r[2],
                         "win_pct": float(r[3]) if r[3] else 0.0} for r in rows]

            # fetching more team stats
            def fetch_team_stats(is_playoffs, min_games):
                rows = conn.execute(text("""
                    SELECT
                        t.name,
                        ROUND(AVG(tbs.points)::numeric, 1)            AS ppg,
                        ROUND(AVG(tbs.offensive_rating)::numeric, 1)  AS ortg,
                        ROUND(AVG(tbs.defensive_rating)::numeric, 1)  AS drtg,
                        ROUND(AVG(tbs.pace)::numeric, 1)              AS pace,
                        COUNT(*) AS gp
                    FROM team_box_scores tbs
                    JOIN teams t ON t.id = tbs.team_id
                    JOIN games g  ON g.id = tbs.game_id
                    WHERE g.season = '2025-26' AND g.is_playoffs = :playoffs
                      AND tbs.offensive_rating IS NOT NULL
                      AND g.nba_game_id NOT LIKE '0062%'
                    GROUP BY t.name
                    HAVING COUNT(*) >= :min_games
                    ORDER BY ppg DESC
                    LIMIT 10
                """), {"playoffs": is_playoffs, "min_games": min_games}).fetchall()
                return [{"name": r[0], "ppg": float(r[1]), "ortg": float(r[2]),
                         "drtg": float(r[3]), "pace": float(r[4]), "gp": r[5]} for r in rows]

            # defining what we return depending on whether we display regular season or playoff stats
            return {
                "regular": {
                    "players":     fetch_players(False, 20),
                    "teams_record": fetch_team_record(False),
                    "teams_stats":  fetch_team_stats(False, 20),
                },
                "playoffs": {
                    "players":     fetch_players(True, 5),
                    "teams_record": fetch_team_record(True),
                    "teams_stats":  fetch_team_stats(True, 5),
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
