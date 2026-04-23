# db_connection.py — sets up the connection to PostgreSQL and provides tools for other files to use

# create_engine is a function that returns a connection object 
from sqlalchemy import create_engine

# sqlalchemy.orm (Object Relational Manager) maps Python objects to database tables
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# reads the database address from .env — format: postgresql+psycopg2://user:password@host:port/dbname
DATABASE_URL = os.getenv("DATABASE_URL")

# the engine is the actual connection to PostgreSQL — everything flows through this
engine = create_engine(DATABASE_URL)

# a factory that creates database sessions on demand
# autocommit=False — changes must be manually saved with db.commit()
# autoflush=False — gives us manual control over when changes are sent to the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# all models (tables) inherit from this — it's what makes SQLAlchemy aware of them
Base = declarative_base()

# called by FastAPI whenever an endpoint needs to talk to the database
# yield hands the session over, and close() runs automatically when the request is done
# like borrowing a library book
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
