# Odds API Betting Utilities

This repository contains a small Python module that wraps [The Odds API](https://the-odds-api.com/)
and provides helper utilities for recording simulated bets.

## Configuration

The API key is expected to be provided via the `ODDS_API` environment variable. The client also
accepts common variants such as `ODDS_API_KEY` or case-insensitive spellings (for example the
`ODDS_APi` secret exposed in GitHub Actions). When running the code locally you can export the
variable before invoking the CLI:

```bash
export ODDS_API="your-key-here"
python -m odds_api.cli sports
```

The hosted environment already exposes the API key through secrets, so no additional configuration
is required.

## Command Line Interface

The CLI exposes three sub-commands:

* `sports` – list available sports. Pass `--all` to include inactive sports.
* `odds` – fetch odds for a specific sport. Use `--regions` and `--markets` to narrow the search.
* `bet` – record a simulated bet. Provide each bet leg as a JSON string with the fields `event_id`,
  `market`, `outcome` and `price`.

Example commands:

```bash
python -m odds_api.cli sports
python -m odds_api.cli odds soccer_epl --regions us --markets h2h
python -m odds_api.cli bet 25 '{"event_id":"game-123","market":"h2h","outcome":"Team A","price":1.95}'
```

The bet command stores wagers in-memory and calculates the potential payout using decimal odds.
In a production system you would replace this with logic that talks to a trading platform or
bookmaker API.

## Running the Tests

Install the dependencies from `requirements.txt` (and optionally `requirements-dev.txt` for
pytest) and then run:

```bash
pytest
```

## Web Interface

A tiny Flask application is included for experimenting in the browser. Install the
dependencies, export your API key, and start the development server:

```bash
export ODDS_API="your-key-here"
python -m odds_api.webapp
```

Visit [http://localhost:8000](http://localhost:8000) to browse the available sports,
inspect current odds, and record simulated bets in-memory. The refreshed interface displays
the odds tables next to a bet slip so you can:

* Populate the slip instantly by clicking **Add** beside an outcome – the event ID, market,
  outcome, and price fields fill in automatically.
* Reset the filter form or the bet slip with a single click when you want to start again.
* See rate limit details and empty states that guide you if no markets are available.
