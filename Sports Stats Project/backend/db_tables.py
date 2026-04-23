# db_tables.py — defines the database tables as Python classes
# each class = one table, each attribute = one column
# all classes inherit from Base so SQLAlchemy knows to treat them as tables

from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.db_connection import Base

class Team(Base):
    __tablename__ = "teams"                                    # the actual table name in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)         # unique ID for each row, auto-incremented
    nba_team_id = Column(Integer, unique=True, index=True)     # the NBA's official team ID from the API
    name = Column(String, unique=True, index=True)             # full team name e.g. "Los Angeles Lakers"
    abbreviation = Column(String, index=True)                  # e.g. "LAL"
    nickname = Column(String)                                  # e.g. "Lakers"
    city = Column(String)
    state = Column(String)
    conference = Column(String)                                # "East" or "West"
    division = Column(String)
    year_founded = Column(Integer)

    # relationships — let us navigate to related objects without writing SQL joins
    players = relationship("Player", back_populates="team")
    home_games = relationship("Game", foreign_keys="Game.home_team_id", back_populates="home_team")
    away_games = relationship("Game", foreign_keys="Game.away_team_id", back_populates="away_team")

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    nba_player_id = Column(Integer, unique=True, index=True)   # the NBA's official player ID
    name = Column(String, index=True)
    first_name = Column(String)
    last_name = Column(String)
    position = Column(String)
    height_inches = Column(Integer)
    weight_lbs = Column(Integer)
    jersey_number = Column(String)
    birthdate = Column(Date, nullable=True)
    country = Column(String, nullable=True)
    school = Column(String, nullable=True)
    draft_year = Column(Integer, nullable=True)
    draft_round = Column(Integer, nullable=True)
    draft_number = Column(Integer, nullable=True)
    season_exp = Column(Integer, nullable=True)                # years of NBA experience
    greatest_75_flag = Column(Boolean, default=False)          # true if named one of NBA's 75 greatest players
    is_active = Column(Boolean, default=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)  # pointer to the teams table

    team = relationship("Team", back_populates="players")
    box_scores = relationship("PlayerBoxScore", back_populates="player")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    nba_game_id = Column(String, unique=True, index=True)      # the NBA's official game ID
    date = Column(Date, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"))     # pointer to the home team
    away_team_id = Column(Integer, ForeignKey("teams.id"))     # pointer to the away team
    home_score = Column(Integer)
    away_score = Column(Integer)
    season = Column(String, index=True)                        # format: "2023-24"
    is_playoffs = Column(Boolean, default=False)

    # two foreign keys pointing to the same table (teams) so we must specify which is which
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_games")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_games")
    player_box_scores = relationship("PlayerBoxScore", back_populates="game")
    team_box_scores = relationship("TeamBoxScore", back_populates="game")

class PlayerBoxScore(Base):
    __tablename__ = "player_box_scores"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))      # which player
    game_id = Column(Integer, ForeignKey("games.id"))          # which game
    team_id = Column(Integer, ForeignKey("teams.id"))          # which team they played for

    # traditional stats
    points = Column(Integer)
    rebounds = Column(Integer)
    assists = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    personal_fouls = Column(Integer)
    minutes_played = Column(Float)

    # shooting breakdown
    fgm = Column(Integer)                                      # field goals made
    fga = Column(Integer)                                      # field goals attempted
    fg3m = Column(Integer)                                     # three pointers made
    fg3a = Column(Integer)                                     # three pointers attempted
    ftm = Column(Integer)                                      # free throws made
    fta = Column(Integer)                                      # free throws attempted

    # advanced stats
    true_shooting_pct = Column(Float)
    usage_rate = Column(Float)
    plus_minus = Column(Integer)
    days_rest = Column(Integer)

    player = relationship("Player", back_populates="box_scores")
    game = relationship("Game", back_populates="player_box_scores")

class TeamBoxScore(Base):
    __tablename__ = "team_box_scores"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    game_id = Column(Integer, ForeignKey("games.id"))

    # advanced team metrics
    offensive_rating = Column(Float)                           # points scored per 100 possessions
    defensive_rating = Column(Float)                           # points allowed per 100 possessions
    pace = Column(Float)                                       # possessions per 48 minutes

    # traditional team stats
    assists = Column(Integer)
    rebounds = Column(Integer)
    turnovers = Column(Integer)
    fgm = Column(Integer)
    fga = Column(Integer)
    fg3m = Column(Integer)
    fg3a = Column(Integer)
    ftm = Column(Integer)
    fta = Column(Integer)
    points = Column(Integer)
    plus_minus = Column(Integer)

    # situational stats — nullable because not always available
    pts_paint = Column(Integer, nullable=True)                 # points in the paint
    pts_2nd_chance = Column(Integer, nullable=True)            # points off offensive rebounds
    pts_fb = Column(Integer, nullable=True)                    # fastbreak points
    largest_lead = Column(Integer, nullable=True)
    lead_changes = Column(Integer, nullable=True)
    times_tied = Column(Integer, nullable=True)

    game = relationship("Game", back_populates="team_box_scores")
