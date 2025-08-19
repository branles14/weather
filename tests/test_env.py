from __future__ import annotations

from pathlib import Path

import pytest

from weather.env import get_owm_token, ensure_owm_token
from weather.core import WeatherError


def test_get_owm_token_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OWM_TOKEN", "abc123")
    assert get_owm_token() == "abc123"


def test_get_owm_token_from_dotenv_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OWM_TOKEN", raising=False)
    dotenv = tmp_path / ".env"
    dotenv.write_text("OWM_TOKEN=fromfile\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert get_owm_token() == "fromfile"


def test_ensure_owm_token_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("OWM_TOKEN", raising=False)
    # Use an empty directory so no stray .env is picked up
    monkeypatch.chdir(tmp_path)
    with pytest.raises(WeatherError):
        ensure_owm_token()


def test_token_from_config_via_xdg(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # No env or .env
    monkeypatch.delenv("OWM_TOKEN", raising=False)
    # Prepare XDG config path with token
    conf_dir = tmp_path / "weather"
    conf_dir.mkdir(parents=True, exist_ok=True)
    (conf_dir / "weather.conf").write_text("OWM_TOKEN=fromconfig\n", encoding="utf-8")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert get_owm_token() == "fromconfig"
