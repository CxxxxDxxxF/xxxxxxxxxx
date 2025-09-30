"""Client helpers for working with The Odds API.

This module provides a small, well-typed wrapper around The Odds API
(`https://the-odds-api.com/`).  Only a subset of the functionality is
required for the project – fetching available sports and retrieving the
latest odds for a specific sport – but the client is written so it can be
extended easily.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Iterable, List, Mapping, MutableMapping, Optional

import requests
from requests import RequestException

__all__ = ["OddsAPIClient", "OddsAPIError", "OddsResponse"]


class OddsAPIError(RuntimeError):
    """Error raised when a call to The Odds API fails."""


@dataclass(slots=True)
class OddsResponse:
    """Container for odds data returned from the API."""

    data: List[MutableMapping[str, object]]
    remaining_requests: Optional[int]
    reset_time: Optional[int]


class OddsAPIClient:
    """A minimal client for The Odds API.

    Parameters
    ----------
    api_key:
        The API key used for authenticating requests.  When ``None`` (the
        default) the client will attempt to load a key from the
        ``ODDS_API`` environment variable.
    session:
        Optional :class:`requests.Session` instance.  Supplying a session
        allows callers to customise transport behaviour (for example for
        timeouts, retries or caching).
    base_url:
        Base URL for the API.  A different URL can be specified when
        working against a mock server in tests.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        session: Optional[requests.Session] = None,
        base_url: str = "https://api.the-odds-api.com/v4",
    ) -> None:
        self._api_key = self._resolve_api_key(api_key)

        self._session = session or requests.Session()
        self._base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def list_sports(self, *, all: bool = False) -> List[MutableMapping[str, object]]:
        """Fetch the list of sports supported by the API."""

        params = {"apiKey": self._api_key}
        if all:
            params["all"] = "true"
        response = self._request("/sports", params=params)
        return response.data

    def get_odds(
        self,
        sport_key: str,
        *,
        regions: Iterable[str] | None = None,
        markets: Iterable[str] | None = None,
        odds_format: str | None = None,
        date_format: str | None = None,
    ) -> OddsResponse:
        """Retrieve odds for a specific sport.

        Parameters mirror those documented by The Odds API and are optional –
        callers can rely on the defaults provided by the service.
        """

        params: MutableMapping[str, object] = {"apiKey": self._api_key}
        if regions:
            params["regions"] = ",".join(regions)
        if markets:
            params["markets"] = ",".join(markets)
        if odds_format:
            params["oddsFormat"] = odds_format
        if date_format:
            params["dateFormat"] = date_format

        response = self._request(f"/sports/{sport_key}/odds", params=params)
        return response

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _request(
        self,
        path: str,
        *,
        params: Optional[Mapping[str, object]] = None,
    ) -> OddsResponse:
        url = f"{self._base_url}{path}"
        try:
            response = self._session.get(url, params=params, timeout=30)
        except RequestException as exc:
            raise OddsAPIError(f"Request to {url} failed: {exc}") from exc
        if response.status_code != 200:
            try:
                payload = response.json()
            except ValueError:  # pragma: no cover - defensive path
                payload = response.text
            raise OddsAPIError(
                f"Request to {url} failed with status {response.status_code}: {payload}"
            )

        try:
            payload = response.json()
        except ValueError as exc:  # pragma: no cover - defensive path
            raise OddsAPIError("API returned invalid JSON") from exc

        remaining_requests = None
        reset_time = None
        if "X-Requests-Remaining" in response.headers:
            remaining_requests = int(response.headers["X-Requests-Remaining"])
        if "X-Requests-Used" in response.headers:
            # Some endpoints use X-Requests-Used / X-Requests-Remaining while
            # others use X-Requests-Remaining / X-Requests-Reset.  Collect what
            # we can.
            try:
                remaining_requests = int(response.headers["X-Requests-Remaining"])
            except (KeyError, ValueError):  # pragma: no cover - defensive
                pass
        if "X-Requests-Reset" in response.headers:
            try:
                reset_time = int(response.headers["X-Requests-Reset"])
            except ValueError:  # pragma: no cover - defensive path
                reset_time = None

        data = payload if isinstance(payload, list) else payload.get("data", payload)
        if not isinstance(data, list):
            raise OddsAPIError(
                "Unexpected response format. Expected a list of odds objects."
            )

        return OddsResponse(data=data, remaining_requests=remaining_requests, reset_time=reset_time)

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _resolve_api_key(explicit_key: Optional[str]) -> str:
        """Return the API key, searching environment variables as needed."""

        if explicit_key:
            return explicit_key

        # Some environments expose secrets with slightly different casing.
        # Honour the documented ``ODDS_API`` name first, then fall back to
        # common variants in a case-insensitive manner.
        preferred_names = ("ODDS_API", "ODDS_API_KEY")
        env = os.environ
        for name in preferred_names:
            value = env.get(name)
            if value:
                return value

        lowered = {name.lower(): value for name, value in env.items() if value}
        for name in preferred_names:
            if name.lower() in lowered:
                return lowered[name.lower()]

        raise OddsAPIError(
            "An API key is required. Set the ODDS_API environment variable "
            "or pass the key explicitly to OddsAPIClient."
        )
