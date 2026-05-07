# Sports Oracle

I am creating a natural language NBA stats platform. Ask any question in plain English; the app uses Claude to generate SQL, queries a PostgreSQL database of real NBA data, and returns results alongside a one-sentence summary.

<img width="1903" height="870" alt="nba website" src="https://github.com/user-attachments/assets/ef097407-54c8-4e02-ae6e-f3acaa7c60bd" />


---

## Features

- **Natural language querying** — type a question like "Who averaged the most points in 2023-24?" and get a real answer
- **AI-powered SQL generation** — Claude (Haiku) reads the database schema and writes the query
- **Natural language summaries** — results are translated back into a plain English sentence
- **Three-mode themes** — Past (blue), Present (purple), Future (green). The past and present functionally work the same, it just keeps data separated. The future will form predicative answers using ML.
- **Animated placeholder** — rotating example questions with a typing animation

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, CSS custom properties |
| Backend | FastAPI, SQLAlchemy, Python |
| Database | PostgreSQL (Docker) |
| AI | Anthropic Claude (Haiku) |
| Data Pipeline | Kaggle CSV dataset, pandas |

---

## Project Structure

```
Sports Stats Project/
├── backend/
│   ├── api_server.py          # FastAPI routes
│   ├── ai_query.py            # Claude SQL generation + summarization
│   ├── db_tables.py           # SQLAlchemy table definitions
│   ├── db_connection.py       # PostgreSQL engine + session
│   ├── data/                  # Kaggle CSV files (not committed)
│   ├── pipeline/
│   │   ├── utils.py                     # Shared helpers (get_season, pad_game_id)
│   │   ├── load_all.py                  # Runs all loaders in order
│   │   ├── load_games.py                # Loads Games.csv
│   │   ├── load_players.py              # Loads Players.csv
│   │   ├── load_player_box_scores.py    # Loads PlayerStatistics.csv
│   │   ├── load_team_box_scores.py      # Loads TeamStatistics.csv
│   │   └── load_awards.py               # Loads Player Award Shares.csv
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/        # Toggle, SearchBar, ResultsTable
│   │   ├── hooks/             # useTheme, useTypingPlaceholder
│   │   ├── api/               # oracle.js (axios wrapper)
│   │   └── styles/            # Per-component CSS
│   └── index.html
├── docker-compose.yml
└── .env
```

---

## Getting Started

### Prerequisites

- Docker Desktop
- Node.js
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Clone the repo

```bash
git clone https://github.com/cargo22/Sports-Oracle.git
cd "Sports Oracle"
```

### 2. Create a `.env` file

```env
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
ANTHROPIC_API_KEY=your_key
DATABASE_URL=postgresql+psycopg2://your_user:your_password@db:5432/your_db
```

### 3. Start the backend

```bash
docker compose up --build
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be running at `http://localhost:5173`.

---

## Data Pipeline

The database is seeded from the [NBA Dataset: Box Scores and Stats (1947 - Today)](https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores) Kaggle dataset, updated daily. I am using the Kaggle API to constantly pull updates made to the dataset.

Download the dataset and place these files in `backend/data/`:
- `PlayerStatistics.csv`
- `TeamStatistics.csv`
- `Games.csv`
- `Players.csv`

To run the full pipeline:

```bash
docker exec sports_backend python pipeline/load_all.py
```

To reload individual tables (e.g. mid-season updates):

```bash
docker exec sports_backend python pipeline/load_games.py
docker exec sports_backend python pipeline/load_player_box_scores.py
```

---

## Example Questions

- Who scored the most points in a single game in 2023-24?
- What was LeBron James' average in the 2021-22 season?
- Which team had the best offensive rating in 2022-23?
- Who led the league in assists per game last season?
