# establishes and defines FastAPI behavior

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

# health check — confirms the server is running
@app.get("/")
def read_root():
    return {"message": "The engine is live!"}

# main endpoint — receives a question, runs the oracle, returns results
@app.post("/ask")
def ask(request: AskRequest):
    try:
        results = run_oracle_query(request.question)
        summarized_result = summarize_results(request.question, results)
        return {"question": request.question, "summary": summarized_result, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # returns error details if something breaks
