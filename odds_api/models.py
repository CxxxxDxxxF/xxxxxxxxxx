"""Data models used by the betting service."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass(slots=True)
class BetLeg:
    """Represents a single selection in a bet."""

    event_id: str
    market: str
    outcome: str
    price: float


@dataclass(slots=True)
class Bet:
    """A minimal in-memory representation of a bet."""

    stake: float
    legs: List[BetLeg]
    id: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    placed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    potential_payout: Optional[float] = None

    def calculate_payout(self) -> float:
        """Calculate the potential payout assuming decimal odds."""

        price = 1.0
        for leg in self.legs:
            price *= leg.price
        payout = round(price * self.stake, 2)
        self.potential_payout = payout
        return payout
