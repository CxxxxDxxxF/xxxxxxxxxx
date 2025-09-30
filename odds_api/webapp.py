"""A tiny Flask interface for interacting with the Odds API tools."""
from __future__ import annotations

from typing import List

from flask import Flask, flash, render_template_string, request

from .client import OddsAPIError
from .models import BetLeg
from .service import BettingService

# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Odds API Demo</title>
    <style>
      :root {
        color-scheme: light dark;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.5;
      }

      body {
        background: rgba(15, 23, 42, 0.04);
        margin: 0;
        min-height: 100vh;
      }

      main {
        margin: 0 auto;
        max-width: 1100px;
        padding: 2.5rem 1.5rem 4rem;
      }

      h1 {
        font-size: clamp(2rem, 1.2rem + 2vw, 3rem);
        margin-bottom: 1.25rem;
        text-align: center;
      }

      p {
        margin: 0 0 1rem;
      }

      a {
        color: inherit;
      }

      .intro {
        margin: 0 auto 2rem;
        max-width: 720px;
        text-align: center;
        color: rgba(15, 23, 42, 0.75);
      }

      .layout {
        display: grid;
        gap: 2rem;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      }

      form {
        background: white;
        border-radius: 1rem;
        box-shadow: 0 1.25rem 3rem -1.5rem rgba(15, 23, 42, 0.4);
        padding: 1.75rem;
      }

      @media (prefers-color-scheme: dark) {
        body {
          background: rgba(15, 23, 42, 0.88);
        }

        form {
          background: rgba(15, 23, 42, 0.7);
          box-shadow: 0 1.5rem 3.5rem -2rem rgba(15, 23, 42, 0.9);
        }

        .intro {
          color: rgba(226, 232, 240, 0.75);
        }
      }

      form h2 {
        margin-top: 0;
        margin-bottom: 0.75rem;
      }

      fieldset {
        border: none;
        margin: 0;
        padding: 0;
      }

      fieldset + fieldset {
        margin-top: 1.25rem;
      }

      label {
        display: block;
        font-weight: 600;
        margin-bottom: 0.35rem;
      }

      .form-help {
        color: rgba(15, 23, 42, 0.6);
        font-size: 0.85rem;
        margin-top: -0.4rem;
        margin-bottom: 0.65rem;
      }

      input[type="text"],
      input[type="number"],
      select {
        border: 1px solid rgba(15, 23, 42, 0.15);
        border-radius: 0.65rem;
        display: block;
        font-size: 1rem;
        margin-bottom: 0.9rem;
        padding: 0.55rem 0.75rem;
        width: 100%;
      }

      .actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-top: 1.25rem;
      }

      button,
      .button-link {
        align-items: center;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        border: none;
        border-radius: 999px;
        color: white;
        cursor: pointer;
        display: inline-flex;
        font-weight: 600;
        gap: 0.5rem;
        justify-content: center;
        padding: 0.65rem 1.5rem;
        text-decoration: none;
        transition: transform 120ms ease, box-shadow 120ms ease;
      }

      button:hover,
      button:focus-visible,
      .button-link:hover,
      .button-link:focus-visible {
        box-shadow: 0 0.75rem 1.5rem -1rem rgba(37, 99, 235, 0.9);
        transform: translateY(-1px);
      }

      button.secondary {
        background: transparent;
        border: 1px solid rgba(37, 99, 235, 0.4);
        color: rgba(37, 99, 235, 0.9);
      }

      .flash {
        border-left: 4px solid;
        border-radius: 0.75rem;
        margin-bottom: 1.25rem;
        padding: 0.9rem 1.1rem;
      }

      .flash--success {
        background: rgba(16, 185, 129, 0.15);
        border-color: rgb(16, 185, 129);
        color: rgb(4, 120, 87);
      }

      .flash--error {
        background: rgba(248, 113, 113, 0.15);
        border-color: rgb(248, 113, 113);
        color: rgb(185, 28, 28);
      }

      .card {
        background: white;
        border-radius: 1rem;
        box-shadow: 0 1.25rem 3rem -1.5rem rgba(15, 23, 42, 0.4);
        margin-top: 2rem;
        overflow: hidden;
      }

      .card__header {
        align-items: baseline;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(37, 99, 235, 0.05));
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        justify-content: space-between;
        padding: 1.25rem 1.5rem;
      }

      .card__title {
        font-size: 1.35rem;
        margin: 0;
      }

      .card__body {
        padding: 1.25rem 1.5rem 1.75rem;
      }

      table {
        border-collapse: collapse;
        width: 100%;
      }

      th,
      td {
        border-bottom: 1px solid rgba(15, 23, 42, 0.12);
        padding: 0.6rem 0.5rem;
        text-align: left;
      }

      tbody tr:last-child td {
        border-bottom: none;
      }

      .outcome-table__actions {
        text-align: right;
      }

      .rate-limit {
        color: rgba(15, 23, 42, 0.65);
        font-size: 0.9rem;
        margin-bottom: 1rem;
      }

      .empty-state {
        align-items: center;
        background: rgba(37, 99, 235, 0.08);
        border-radius: 0.85rem;
        color: rgba(15, 23, 42, 0.72);
        display: flex;
        gap: 0.75rem;
        justify-content: center;
        padding: 2rem 1.25rem;
        text-align: center;
      }

      .bets {
        margin-top: 2.5rem;
      }

      .bets table th,
      .bets table td {
        vertical-align: top;
      }

      .bet-leg-list {
        margin: 0;
        padding-left: 1.2rem;
      }

      .subdued {
        color: rgba(15, 23, 42, 0.6);
      }

      @media (prefers-color-scheme: dark) {
        th,
        td,
        .rate-limit,
        .empty-state,
        .form-help,
        .subdued {
          color: rgba(226, 232, 240, 0.8);
        }

        table {
          color: rgba(226, 232, 240, 0.92);
        }

        button.secondary {
          color: rgba(191, 219, 254, 0.92);
        }
      }
    </style>
  </head>
  <body>
    <main>
      <h1>Odds API playground</h1>
      <p class="intro">Browse the available sports, pull live odds, and build a one-leg sample bet to see the projected payout. Use the buttons next to an outcome to pre-fill the bet slip instantly.</p>

      {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
          {% for category, text in messages %}
            <div class="flash flash--{{ category }}">{{ text }}</div>
          {% endfor %}
        {% endif %}
      {% endwith %}

      <div class="layout">
        <form method="get" action="{{ url_for('index') }}">
          <h2>Browse odds</h2>
          <fieldset>
            <label for="sport">Sport</label>
            <select name="sport" id="sport">
              <option value="" disabled {% if not selected_sport %}selected{% endif %}>Select a sport…</option>
              {% for sport in sports %}
                {% set key = sport.get('key') %}
                {% set label = sport.get('title') or key %}
                <option value="{{ key }}" {% if key == selected_sport %}selected{% endif %}>{{ label }}</option>
              {% endfor %}
            </select>
            <p class="form-help">Odds refresh when you submit the form. If you leave the filters blank the defaults recommended by The Odds API are used.</p>
          </fieldset>

          <fieldset>
            <label for="regions">Regions</label>
            <input type="text" name="regions" id="regions" value="{{ regions_value }}" placeholder="us,uk">
            <p class="form-help">Comma separated list of regions to query (e.g. <code>us,uk</code>).</p>
          </fieldset>

          <fieldset>
            <label for="markets">Markets</label>
            <input type="text" name="markets" id="markets" value="{{ markets_value }}" placeholder="h2h,spreads,totals">
            <p class="form-help">Comma separated list of markets such as <code>h2h</code> (moneyline) or <code>totals</code>.</p>
          </fieldset>

          <div class="actions">
            <button type="submit">Fetch odds</button>
            <button type="reset" class="secondary" onclick="window.location='{{ url_for('index') }}'">Reset filters</button>
          </div>
        </form>

        <form method="post" action="{{ url_for('index') }}" id="bet-form">
          <h2>Bet slip</h2>
          <p class="form-help">This creates a simulated, single-leg bet in memory only.</p>

          <input type="hidden" name="sport" value="{{ selected_sport }}">
          <input type="hidden" name="regions" value="{{ regions_value }}">
          <input type="hidden" name="markets" value="{{ markets_value }}">

          <label for="stake">Stake</label>
          <input type="number" name="stake" id="stake" step="0.01" min="0" placeholder="Enter wager amount" required>

          <label for="event_id">Event ID</label>
          <input type="text" name="event_id" id="event_id" placeholder="Select an outcome below or paste an ID" required>

          <label for="market">Market</label>
          <input type="text" name="market" id="market" placeholder="h2h" required>

          <label for="outcome">Outcome</label>
          <input type="text" name="outcome" id="outcome" placeholder="Moneyline team or prop" required>

          <label for="price">Decimal price</label>
          <input type="number" name="price" id="price" step="0.01" min="1" placeholder="1.90" required>

          <div class="actions">
            <button type="submit">Record bet</button>
            <button type="button" class="secondary" id="clear-bet">Clear</button>
          </div>
        </form>
      </div>

      <section class="card">
        <div class="card__header">
          <h2 class="card__title">Available events</h2>
          <div class="rate-limit">
            {% if selected_sport %}
              <span class="subdued">Showing odds for <strong>{{ selected_sport }}</strong></span>
            {% else %}
              <span class="subdued">Choose a sport to load the latest markets.</span>
            {% endif %}
            {% if remaining_requests is not none %}
              &nbsp;•&nbsp; Requests remaining: {{ remaining_requests }}
            {% endif %}
            {% if reset_time is not none %}
              &nbsp;•&nbsp; Resets at UNIX {{ reset_time }}
            {% endif %}
          </div>
        </div>
        <div class="card__body">
          {% if odds is none %}
            <div class="empty-state">Pick a sport and click <strong>Fetch odds</strong> to see events here.</div>
          {% elif odds %}
            {% for event in odds %}
              <article style="margin-bottom: 2rem;">
                <header style="margin-bottom: 0.5rem;">
                  <h3 style="margin: 0;">{{ event.get('home_team', 'Home') }} vs {{ event.get('away_team', 'Away') }}</h3>
                  <p class="subdued" style="margin: 0.35rem 0 0;">Event ID {{ event.get('id', 'n/a') }} • Commences {{ event.get('commence_time', 'n/a') }}</p>
                </header>

                {% if event.get('bookmakers') %}
                  <div style="overflow-x: auto;">
                    <table class="outcome-table">
                      <thead>
                        <tr>
                          <th scope="col">Bookmaker</th>
                          <th scope="col">Market</th>
                          <th scope="col">Outcome</th>
                          <th scope="col">Price</th>
                          <th scope="col" class="outcome-table__actions">Add to bet slip</th>
                        </tr>
                      </thead>
                      <tbody>
                        {% for bookmaker in event.get('bookmakers', []) %}
                          {% for market in bookmaker.get('markets', []) %}
                            {% for outcome in market.get('outcomes', []) %}
                              <tr data-event="{{ event.get('id', '') }}" data-market="{{ market.get('key') }}" data-outcome="{{ outcome.get('name') }}" data-price="{{ outcome.get('price') }}">
                                <td>{{ bookmaker.get('title', bookmaker.get('key')) }}</td>
                                <td>{{ market.get('key') }}</td>
                                <td>{{ outcome.get('name') }}</td>
                                <td>{{ outcome.get('price') }}</td>
                                <td class="outcome-table__actions"><button type="button" class="secondary" data-action="add-leg">Add</button></td>
                              </tr>
                            {% endfor %}
                          {% endfor %}
                        {% endfor %}
                      </tbody>
                    </table>
                  </div>
                {% else %}
                  <p class="empty-state" style="margin: 0;">No bookmaker pricing returned for this event.</p>
                {% endif %}
              </article>
            {% endfor %}
          {% else %}
            <div class="empty-state">No events were returned for the current filters. Try another market or region.</div>
          {% endif %}
        </div>
      </section>

      <section class="card bets">
        <div class="card__header">
          <h2 class="card__title">Recorded bets</h2>
          <p class="subdued" style="margin: 0;">These bets are stored in memory and reset when the server restarts.</p>
        </div>
        <div class="card__body">
          {% if bets %}
            <div style="overflow-x: auto;">
              <table>
                <thead>
                  <tr>
                    <th>Placed at</th>
                    <th>Stake</th>
                    <th>Potential payout</th>
                    <th>Legs</th>
                  </tr>
                </thead>
                <tbody>
                  {% for bet in bets %}
                    <tr>
                      <td>{{ bet.placed_at }}</td>
                      <td>{{ "%.2f"|format(bet.stake) }}</td>
                      <td>{{ "%.2f"|format(bet.potential_payout or 0) }}</td>
                      <td>
                        <ul class="bet-leg-list">
                          {% for leg in bet.legs %}
                            <li>{{ leg.event_id }} – {{ leg.market }} – {{ leg.outcome }} @ {{ leg.price }}</li>
                          {% endfor %}
                        </ul>
                      </td>
                    </tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
          {% else %}
            <div class="empty-state">No bets recorded yet. Use the bet slip on the right to create one.</div>
          {% endif %}
        </div>
      </section>
    </main>

    <script>
      const betForm = document.getElementById('bet-form');
      const stakeInput = document.getElementById('stake');
      const eventInput = document.getElementById('event_id');
      const marketInput = document.getElementById('market');
      const outcomeInput = document.getElementById('outcome');
      const priceInput = document.getElementById('price');
      const clearButton = document.getElementById('clear-bet');

      document.querySelectorAll('[data-action="add-leg"]').forEach((button) => {
        button.addEventListener('click', () => {
          const row = button.closest('tr');
          if (!row) {
            return;
          }

          eventInput.value = row.dataset.event || '';
          marketInput.value = row.dataset.market || '';
          outcomeInput.value = row.dataset.outcome || '';
          priceInput.value = row.dataset.price || '';

          if (!stakeInput.value) {
            stakeInput.focus();
          } else {
            priceInput.focus();
          }
        });
      });

      clearButton?.addEventListener('click', () => {
        betForm.reset();
        stakeInput.focus();
      });
    </script>
  </body>
</html>
"""


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def _split_csv(value: str | None) -> List[str] | None:
    if not value:
        return None
    items = [part.strip() for part in value.split(",")]
    return [item for item in items if item]


def create_app(service: BettingService | None = None) -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)
    app.secret_key = "odds-api-demo"
    if service is not None:
        app.config["BETTING_SERVICE"] = service

    @app.route("/", methods=["GET", "POST"])
    def index() -> str:
        betting_service: BettingService | None = None
        error_message = None
        try:
            if service is not None:
                betting_service = service
            else:
                betting_service = app.config.get("BETTING_SERVICE")
                if betting_service is None:
                    betting_service = BettingService.from_environment()
                    app.config["BETTING_SERVICE"] = betting_service
        except OddsAPIError as exc:
            error_message = str(exc)

        selected_sport = (request.values.get("sport") or "").strip()
        regions_value = (request.values.get("regions") or "us").strip()
        markets_value = (request.values.get("markets") or "h2h").strip()

        odds_response = None

        if request.method == "POST" and betting_service is not None:
            try:
                stake = float(request.form["stake"])
                event_id = request.form["event_id"].strip()
                market = request.form["market"].strip()
                outcome = request.form["outcome"].strip()
                price = float(request.form["price"])

                if not all([event_id, market, outcome]):
                    raise ValueError("All bet fields are required.")

                leg = BetLeg(
                    event_id=event_id,
                    market=market,
                    outcome=outcome,
                    price=price,
                )
                bet = betting_service.place_bet(stake, [leg])
                flash(
                    f"Bet recorded! Potential payout: {bet.potential_payout:.2f}",
                    category="success",
                )
            except (KeyError, ValueError) as exc:
                error_message = str(exc)
            except OddsAPIError as exc:
                error_message = str(exc)

        sports = []
        if betting_service is not None:
            try:
                sports = betting_service.fetch_sports()
            except OddsAPIError as exc:
                error_message = error_message or str(exc)

            if selected_sport:
                try:
                    odds_response = betting_service.fetch_odds(
                        selected_sport,
                        regions=_split_csv(regions_value) or None,
                        markets=_split_csv(markets_value) or None,
                    )
                except OddsAPIError as exc:
                    odds_response = None
                    error_message = error_message or str(exc)

        if error_message:
            flash(error_message, category="error")

        bets = betting_service.list_bets() if betting_service is not None else []

        return render_template_string(
            TEMPLATE,
            sports=sports,
            selected_sport=selected_sport,
            regions_value=regions_value,
            markets_value=markets_value,
            odds=(odds_response.data if odds_response else None),
            remaining_requests=(
                odds_response.remaining_requests if odds_response else None
            ),
            reset_time=(odds_response.reset_time if odds_response else None),
            bets=bets,
        )

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover - convenience for manual runs
    app.run(host="0.0.0.0", port=8000, debug=True)

