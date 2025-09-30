from __future__ import annotations

from dataclasses import dataclass
from typing import List, MutableMapping

import pytest

from odds_api.models import BetLeg
from odds_api.service import BettingService


@dataclass
class _FakeResponse:
    data: List[MutableMapping[str, object]]
    remaining_requests: int | None = None
    reset_time: int | None = None


class _FakeClient:
    def __init__(self) -> None:
        self.list_calls = 0
        self.odds_calls = []

    def list_sports(self, *, all: bool = False):
        self.list_calls += 1
        assert isinstance(all, bool)
        return [{"key": "soccer_epl"}, {"key": "basketball_nba"}]

    def get_odds(self, sport_key: str, **kwargs):
        self.odds_calls.append((sport_key, kwargs))
        return _FakeResponse(
            data=[{"id": "game-1", "bookmakers": []}],
            remaining_requests=10,
            reset_time=123,
        )


def test_fetch_sports_calls_client():
    service = BettingService(client=_FakeClient())
    sports = service.fetch_sports()
    assert {sport["key"] for sport in sports} == {"soccer_epl", "basketball_nba"}


def test_fetch_odds_forwards_arguments():
    client = _FakeClient()
    service = BettingService(client=client)
    response = service.fetch_odds("soccer_epl", regions=["us"], markets=["h2h"])
    assert response.remaining_requests == 10
    assert client.odds_calls == [("soccer_epl", {"regions": ["us"], "markets": ["h2h"]})]


def test_place_bet_calculates_payout():
    client = _FakeClient()
    service = BettingService(client=client)
    legs = [
        BetLeg(event_id="game-1", market="h2h", outcome="Team A", price=1.9),
        BetLeg(event_id="game-2", market="h2h", outcome="Team B", price=1.85),
    ]
    bet = service.place_bet(stake=25.0, legs=legs)
    assert bet.potential_payout == pytest.approx(25.0 * 1.9 * 1.85, rel=1e-4)
    assert service.list_bets() == [bet]
