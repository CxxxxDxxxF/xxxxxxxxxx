"""Utilities for interacting with The Odds API and managing bets."""

from .client import OddsAPIClient, OddsAPIError
from .models import Bet, BetLeg
from .service import BettingService

__all__ = [
    "OddsAPIClient",
    "OddsAPIError",
    "BettingService",
    "Bet",
    "BetLeg",
]
