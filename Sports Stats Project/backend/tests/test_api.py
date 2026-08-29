# test_api.py - file meant for testing API backend

from fastapi.testclient import TestClient
from api_server import app
import pytest

# TestClient is a FastAPI class that lets us test FastAPI applications without having
# a live server connection
client = TestClient(app)
response = client.get("/api/leaders")
data = response.json()

@pytest.fixture
def leaders():
    response = client.get("/api/leaders")
    return response.json()


def test_health_check():
    # the simplest possible test: GET / should say the engine is live
    response = client.get("/")

    # assert = "this must be true, or fail the test"
    assert response.status_code == 200
    assert response.json() == {"message": "The engine is live!"}

def test_leaders_returns_ok():
    assert response.status_code == 200

def test_leaders_has_both_sections(leaders):
    assert "regular" in leaders
    assert "playoffs" in leaders

def test_no_team_exceeds_16_playoff_wins():
    records = data["playoffs"]["teams_record"]

    for team in records:
        assert team["wins"] <= 16

def test_players_sorted_by_ppg():
    players = data["regular"]["players"]

    for i in range(len(players) - 1):
        assert players[i]["ppg"] >= players[i + 1]["ppg"]

def test_win_pct_in_valid_range():
    records = data["regular"]["teams_record"]

    for team in records:
        assert 0 <= team["win_pct"] <= 1