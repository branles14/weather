"""Configuration parser for the weather utility."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path.home() / ".config/weather.conf"
VALID_UNITS = {"metric", "imperial", "standard"}


@dataclass
class Config:
    """Simple representation of the configuration file."""

    lat: Optional[float] = None
    lon: Optional[float] = None
    units: Optional[str] = None


def load_config(path: Path = CONFIG_PATH) -> Config:
    """Load configuration from *path*.

    Parameters
    ----------
    path:
        Location of the configuration file. Defaults to
        ``~/.config/weather.conf``.
    """

    cfg = Config()
    if not path.is_file():
        return cfg

    for line in path.read_text(encoding="utf-8").splitlines():
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
    return cfg
