from __future__ import annotations

from typing import List

import pytest

from odds_api.client import OddsResponse
from odds_api.models import Bet
from odds_api.webapp import create_app


class DummyService:
    def __init__(self) -> None:
        self._bets: List[Bet] = []
        self._sports = [
            {"key": "soccer_epl", "title": "EPL Soccer"},
            {"key": "basketball_nba", "title": "NBA"},
        ]
        self._odds = OddsResponse(
            data=[
                {
                    "id": "match-1",
                    "home_team": "Team A",
                    "away_team": "Team B",
                    "commence_time": "2024-01-01T12:00:00Z",
                    "bookmakers": [
                        {
                            "title": "DemoBook",
                            "key": "demo",
                            "markets": [
                                {
                                    "key": "h2h",
                                    "outcomes": [
                                        {"name": "Team A", "price": 1.9},
                                        {"name": "Team B", "price": 2.1},
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
            remaining_requests=7,
            reset_time=1234567890,
        )

    def fetch_sports(self, *, include_inactive: bool = False):
        return self._sports

    def fetch_odds(self, sport_key: str, **_: object):
        return self._odds

    def place_bet(self, stake: float, legs):
        bet = Bet(stake=stake, legs=list(legs))
        bet.calculate_payout()
        self._bets.append(bet)
        return bet

    def list_bets(self):
        return list(self._bets)


@pytest.fixture()
def client():
    service = DummyService()
    app = create_app(service=service)
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_index_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Odds API playground" in body
    assert "Select a sport" in body


def test_fetch_odds_displays_events(client):
    response = client.get("/?sport=soccer_epl&regions=us&markets=h2h")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Team A vs Team B" in body
    assert "DemoBook" in body
    assert "Requests remaining: 7" in body
    assert "Add to bet slip" in body


def test_place_bet_records_entry(client):
    form_data = {
        "stake": "10",
        "event_id": "match-1",
        "market": "h2h",
        "outcome": "Team A",
        "price": "1.9",
    }
    response = client.post("/", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Bet recorded! Potential payout" in body
    assert "match-1" in body
