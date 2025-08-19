"""Environment variable handling for the weather utility.

This module centralizes reading environment variables and simple `.env`
files so other parts of the application do not need to manually parse
environment state. It keeps behavior predictable and errors clear.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Dict, Optional

from .core import WeatherError
from .config import load_config


DOTENV_FILENAMES = (".env",)


def _package_root() -> Path:
    """Return the package root directory (project root during development).

    When installed as a package, this points to the installed location; in
    development it resolves to the repository root.
    """
    return Path(__file__).resolve().parent.parent


def _parse_dotenv(path: Path) -> Dict[str, str]:
    """Parse a dotenv-style file into a dict.

    Lines must be of the form ``KEY=VALUE`` with optional whitespace. Empty
    lines and comments starting with ``#`` are ignored. No shell expansion is
    performed.
    """
    if not path.is_file():
        return {}
    result: Dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def _load_dotenv() -> Dict[str, str]:
    """Load dotenv variables from CWD and package root, CWD has priority."""
    data: Dict[str, str] = {}
    # Highest priority: current working directory
    for name in DOTENV_FILENAMES:
        data.update(_parse_dotenv(Path.cwd() / name))
    # Next: repository/package root (useful during development)
    for name in DOTENV_FILENAMES:
        data.update(_parse_dotenv(_package_root() / name))
    return data


def get_owm_token() -> Optional[str]:
    """Return the OpenWeatherMap API token from env or .env.

    Precedence:
    1) ``OWM_TOKEN`` from process environment.
    2) ``OWM_TOKEN`` in `.env` (CWD, then package root).
    """
    token = os.environ.get("OWM_TOKEN")
    if token:
        return token
    dotenv = _load_dotenv()
    if "OWM_TOKEN" in dotenv:
        return dotenv.get("OWM_TOKEN")
    # Fall back to configuration file
    cfg = load_config()
    return cfg.token


def ensure_owm_token() -> str:
    """Return a valid OWM token or raise a friendly error.

    Raises
    ------
    WeatherError
        When no token can be found in ``OWM_TOKEN`` or `.env`.
    """
    token = get_owm_token()
    if not token:
        raise WeatherError(
            "No OpenWeatherMap token found. Set OWM_TOKEN or add OWM_TOKEN=... to .env"
        )
    return token


@dataclass
class EnvLocation:
    latitude: Optional[float]
    longitude: Optional[float]


def get_env_location() -> EnvLocation:
    """Return latitude/longitude from environment variables, if any.

    This helper does not raise on partial values; it simply converts present
    values and leaves missing ones as ``None``. Use higher-level validation to
    enforce both-present semantics where needed.
    """
    lat = os.environ.get("LATITUDE")
    lon = os.environ.get("LONGITUDE")
    lat_f = float(lat) if lat not in (None, "") else None
    lon_f = float(lon) if lon not in (None, "") else None
    return EnvLocation(latitude=lat_f, longitude=lon_f)


__all__ = [
    "get_owm_token",
    "ensure_owm_token",
    "get_env_location",
    "EnvLocation",
]
