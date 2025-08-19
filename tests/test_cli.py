from __future__ import annotations

from typing import Any

import json
from click.testing import CliRunner
import pytest

from weather.cli import main


def test_cli_errors_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    monkeypatch.delenv("OWM_TOKEN", raising=False)
    result = runner.invoke(main, [])
    assert result.exit_code != 0
    assert "token" in result.output.lower()


def test_cli_uses_cache_and_exits_ok(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    # Provide env token so CLI passes token check
    monkeypatch.setenv("OWM_TOKEN", "dummy")

    # Patch cache path and read_cache to return a valid structure
    from weather import core as core_mod
    from weather.core import update as update_mod

    sample = {"lat": 10.0, "lon": 20.0, "current": {"dt": 9999999999}}

    monkeypatch.setattr(update_mod, "cache_file", lambda: tmp_path / "weather.json")
    monkeypatch.setattr(update_mod, "read_cache", lambda *a, **k: sample)
    # Avoid any network call via fetch_weather if it would be reached
    monkeypatch.setattr(update_mod, "fetch_weather", lambda *a, **k: sample)

    # Provide explicit location via args to avoid other resolvers
    runner = CliRunner()
    result = runner.invoke(main, ["--lat", "10", "--lon", "20"]) 
    assert result.exit_code == 0
    # Output should be a one-line JSON object
    out = result.output.strip()
    parsed = json.loads(out)
    assert parsed["lat"] == 10.0 and parsed["lon"] == 20.0

