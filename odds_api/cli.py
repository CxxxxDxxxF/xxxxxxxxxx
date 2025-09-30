"""Command line helpers for fetching odds and placing bets."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .models import BetLeg
from .service import BettingService


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interact with The Odds API")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sports_parser = subparsers.add_parser("sports", help="List available sports")
    sports_parser.add_argument(
        "--all",
        action="store_true",
        help="Include sports that are not currently in season",
    )

    odds_parser = subparsers.add_parser("odds", help="Fetch odds for a sport")
    odds_parser.add_argument("sport", help="Sport key (see the sports command)")
    odds_parser.add_argument("--regions", nargs="*", help="Regions to filter (comma separated)")
    odds_parser.add_argument("--markets", nargs="*", help="Markets to include")
    odds_parser.add_argument(
        "--odds-format",
        choices=["american", "decimal"],
        help="Preferred odds format",
    )

    bet_parser = subparsers.add_parser("bet", help="Record a simulated bet")
    bet_parser.add_argument("stake", type=float, help="Stake size")
    bet_parser.add_argument(
        "legs",
        type=str,
        nargs="+",
        help=(
            "JSON encoded bet legs with keys event_id, market, outcome and price. "
            "Example: '{"event_id":"sp:1", "market":"h2h", "outcome":"Team A", "price":1.9}'"
        ),
    )

    return parser


def _print(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2, sort_keys=True, default=str)
    sys.stdout.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    service = BettingService.from_environment()

    if args.command == "sports":
        sports = service.fetch_sports(include_inactive=args.all)
        _print(sports)
        return 0

    if args.command == "odds":
        response = service.fetch_odds(
            args.sport,
            regions=args.regions,
            markets=args.markets,
            odds_format=args.odds_format,
        )
        payload = {
            "data": response.data,
            "remaining_requests": response.remaining_requests,
            "reset_time": response.reset_time,
        }
        _print(payload)
        return 0

    if args.command == "bet":
        legs = []
        for leg_payload in args.legs:
            leg_data = json.loads(leg_payload)
            leg = BetLeg(
                event_id=leg_data["event_id"],
                market=leg_data["market"],
                outcome=leg_data["outcome"],
                price=float(leg_data["price"]),
            )
            legs.append(leg)
        bet = service.place_bet(stake=args.stake, legs=legs)
        _print({
            "bet_id": bet.id,
            "stake": bet.stake,
            "potential_payout": bet.potential_payout,
            "placed_at": bet.placed_at,
            "legs": [leg.__dict__ for leg in bet.legs],
        })
        return 0

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
