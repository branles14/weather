"""Weather data retrieval and caching."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional
from urllib.error import URLError
from urllib.request import urlopen

from . import WeatherError


DEFAULT_MAX_AGE = 300
DEFAULT_MAX_RANGE = 1000


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in meters between two points."""
    from math import radians, cos, sin, asin, sqrt

    r = 6371000.0  # Earth radius in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * r * asin(sqrt(a))


def cache_file() -> Path:
    """Return the path of the cache file, ensuring the directory exists."""
    storage = os.environ.get("STORAGE")
    base = (
        Path(storage)
        if storage and os.path.isdir(storage) and os.access(storage, os.W_OK)
        else Path.home()
    )
    cache_dir = base / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "weather.json"


def read_cache(
    path: Path,
    lat: float,
    lon: float,
    max_range: int = DEFAULT_MAX_RANGE,
    max_age: int = DEFAULT_MAX_AGE,
) -> Optional[dict]:
    """Return cached data if it's close enough and recent.

    Parameters
    ----------
    path:
        Location of the cached JSON file.
    lat, lon:
        Target coordinates used to validate the cache.
    max_range:
        Maximum allowed distance in meters between the cache coordinates and the
        requested coordinates. Negative values disable the check.
    max_age:
        Maximum cache age in seconds.
    """
    if not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError:
        return None

    if max_range >= 0:
        cached_lat = data.get("lat")
        cached_lon = data.get("lon")
        if not isinstance(cached_lat, (int, float)) or not isinstance(
            cached_lon, (int, float)
        ):
            return None
        if _haversine_m(lat, lon, float(cached_lat), float(cached_lon)) > max_range:
            return None

    dt = data.get("current", {}).get("dt")
    if not isinstance(dt, (int, float)):
        return None
    if time.time() - dt > max_age:
        return None
    return data


def fetch_weather(
    lat: float, lon: float, units: str, token: str, path: Path, verbose: bool = False
) -> dict:
    """Fetch fresh weather data from OpenWeatherMap and update the cache."""
    url = (
        "https://api.openweathermap.org/data/3.0/onecall"
        f"?lat={lat}&lon={lon}&appid={token}&units={units}"
    )
    if verbose:
        print("Requesting data from OpenWeatherMap", file=os.sys.stderr)
    try:
        with urlopen(url) as resp:
            data = json.load(resp)
    except URLError as exc:
        raise WeatherError("Failed to retrieve weather data") from exc

    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh)
    return data


__all__ = [
    "cache_file",
    "read_cache",
    "fetch_weather",
    "DEFAULT_MAX_AGE",
    "DEFAULT_MAX_RANGE",
]
