# establishes and defines FastAPI behavior

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import backend.db_tables as db_tables
from backend.db_connection import engine
from backend.ai_query import run_oracle_query

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

# health check — confirms the server is running
@app.get("/")
def read_root():
    return {"message": "The engine is live!"}

# main endpoint — receives a question, runs the oracle, returns results
@app.post("/ask")
def ask(request: AskRequest):
    try:
        results = run_oracle_query(request.question)
        return {"question": request.question, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # returns error details if something breaks
