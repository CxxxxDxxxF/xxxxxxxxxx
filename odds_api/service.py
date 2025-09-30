"""High level betting workflow utilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from .client import OddsAPIClient, OddsResponse
from .models import Bet, BetLeg


@dataclass(slots=True)
class BettingService:
    """Coordinate fetching odds and recording bets."""

    client: OddsAPIClient
    _bets: List[Bet] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Odds helpers
    # ------------------------------------------------------------------
    def fetch_sports(self, *, include_inactive: bool = False) -> List[dict[str, object]]:
        """Return the sports currently available from the API."""

        return self.client.list_sports(all=include_inactive)

    def fetch_odds(
        self,
        sport_key: str,
        *,
        regions: Iterable[str] | None = None,
        markets: Iterable[str] | None = None,
        odds_format: str | None = None,
    ) -> OddsResponse:
        """Fetch the latest odds for a given sport."""

        kwargs = {}
        if regions is not None:
            kwargs["regions"] = regions
        if markets is not None:
            kwargs["markets"] = markets
        if odds_format is not None:
            kwargs["odds_format"] = odds_format

        return self.client.get_odds(sport_key, **kwargs)

    # ------------------------------------------------------------------
    # Betting helpers
    # ------------------------------------------------------------------
    def place_bet(self, stake: float, legs: Iterable[BetLeg]) -> Bet:
        """Create a bet based on the provided stake and legs.

        The function calculates the potential payout (assuming decimal odds)
        and stores the bet in memory.  In a real-world application this is
        where you would call into a trading service or bookmaker.
        """

        bet = Bet(stake=stake, legs=list(legs))
        bet.calculate_payout()
        self._bets.append(bet)
        return bet

    def list_bets(self) -> List[Bet]:
        """Return the bets recorded in memory."""

        return list(self._bets)

    # ------------------------------------------------------------------
    # Convenience constructors
    # ------------------------------------------------------------------
    @classmethod
    def from_environment(cls) -> "BettingService":
        """Create a service using the ``ODDS_API`` environment variable."""

        client = OddsAPIClient()
        return cls(client)
