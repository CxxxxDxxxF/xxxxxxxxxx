from __future__ import annotations

from typing import Any, Dict, Optional

import pytest

from odds_api.client import OddsAPIClient, OddsAPIError


class _FakeResponse:
    def __init__(self, payload: Any) -> None:
        self.status_code = 200
        self._payload = payload
        self.headers: Dict[str, str] = {}

    def json(self) -> Any:  # pragma: no cover - simple passthrough
        return self._payload


class _RecordingSession:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Optional[dict[str, object]], Optional[int]]] = []

    def get(self, url: str, params: Optional[dict[str, object]] = None, timeout: Optional[int] = None):
        self.calls.append((url, params, timeout))
        return _FakeResponse([])


def test_client_accepts_case_insensitive_environment_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ODDS_API", raising=False)
    monkeypatch.delenv("ODDS_API_KEY", raising=False)
    monkeypatch.setenv("ODDS_APi", "secret-key")

    session = _RecordingSession()
    client = OddsAPIClient(session=session, base_url="https://example.com")

    client.list_sports()
    assert session.calls == [
        (
            "https://example.com/sports",
            {"apiKey": "secret-key"},
            30,
        )
    ]


def test_client_raises_error_when_no_key_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ODDS_API", raising=False)
    monkeypatch.delenv("ODDS_API_KEY", raising=False)
    monkeypatch.delenv("ODDS_APi", raising=False)

    with pytest.raises(OddsAPIError):
        OddsAPIClient(session=_RecordingSession(), base_url="https://example.com")
