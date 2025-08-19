"""Configuration parser for the weather utility.

Supports XDG-style configuration at:
- ``$XDG_CONFIG_HOME/weather/weather.conf`` (preferred)
- ``~/.config/weather/weather.conf``

For backward compatibility it also accepts the legacy path:
- ``~/.config/weather.conf``

The parser also accepts an explicit path argument for testing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VALID_UNITS = {"metric", "imperial", "standard"}


def _xdg_config_home() -> Path:
    """Return the XDG config home directory.

    Respects ``$XDG_CONFIG_HOME`` with fallback to ``~/.config``.
    """
    env = os.environ.get("XDG_CONFIG_HOME")
    return Path(env).expanduser() if env else Path.home() / ".config"


def _candidate_paths() -> list[Path]:
    """Return config search paths in priority order."""
    xdg = _xdg_config_home()
    return [
        xdg / "weather/weather.conf",  # preferred location
        Path.home() / ".config/weather/weather.conf",  # fallback
        Path.home() / ".config/weather.conf",  # legacy
    ]


@dataclass
class Config:
    """Simple representation of the configuration file."""

    lat: Optional[float] = None
    lon: Optional[float] = None
    units: Optional[str] = None
    cache_max_range: Optional[int] = None
    cache_max_age: Optional[int] = None
    token: Optional[str] = None


def load_config(path: Optional[Path] = None) -> Config:
    """Load configuration from a path or known locations.

    If ``path`` is supplied it is used directly. Otherwise the first existing
    file found in the candidate path list is loaded. Missing files yield an
    empty ``Config``.
    """
    cfg = Config()

    if path is None:
        for candidate in _candidate_paths():
            if candidate.is_file():
                path = candidate
                break

    if path is None or not Path(path).is_file():
        return cfg

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().upper()
        value = value.strip()

        if key in {"LAT", "LATITUDE"}:
            try:
                cfg.lat = float(value)
            except ValueError as exc:
                raise ValueError(f"Invalid latitude value: {value}") from exc
        elif key in {"LON", "LONGITUDE"}:
            try:
                cfg.lon = float(value)
            except ValueError as exc:
                raise ValueError(f"Invalid longitude value: {value}") from exc
        elif key == "UNITS":
            if value:
                val = value.lower()
                if val not in VALID_UNITS:
                    raise ValueError(f"Invalid units value: {value}")
                cfg.units = val
        elif key == "CACHE_MAX_RANGE":
            try:
                cfg.cache_max_range = int(value)
            except ValueError as exc:
                raise ValueError(f"Invalid CACHE_MAX_RANGE value: {value}") from exc
        elif key == "CACHE_MAX_AGE":
            try:
                cfg.cache_max_age = int(value)
            except ValueError as exc:
                raise ValueError(f"Invalid CACHE_MAX_AGE value: {value}") from exc
        elif key in {"OWM_TOKEN", "TOKEN"}:  # TOKEN accepted for legacy compatibility
            if value:
                cfg.token = value
    return cfg
