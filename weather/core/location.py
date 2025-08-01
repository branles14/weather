"""Location resolution helpers."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Optional, Tuple
from urllib.error import URLError
from urllib.request import urlopen

from ..config import load_config
from . import WeatherError


def _geocode_city(city: str, token: str) -> Tuple[float, float]:
    """Resolve *city* name to latitude and longitude using OpenWeatherMap."""
    url = (
        f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={token}"
    )
    try:
        with urlopen(url) as resp:
            results = json.load(resp)
    except URLError as exc:
        raise WeatherError("Failed to resolve city name") from exc
    if not results:
        raise WeatherError("City not found")
    lat = float(results[0]["lat"])
    lon = float(results[0]["lon"])
    return round(lat, 4), round(lon, 4)


def _location_from_env() -> Optional[Tuple[float, float]]:
    """Return coordinates from `$LATITUDE` and `$LONGITUDE` if both are set.

    Raises `WeatherError` when only one of the variables is defined,
    otherwise returns ``None`` when neither is present.
    """
    lat = os.environ.get("LATITUDE")
    lon = os.environ.get("LONGITUDE")
    if lat and lon:
        try:
            return float(lat), float(lon)
        except ValueError:
            raise WeatherError("Invalid LATITUDE or LONGITUDE value")
    if lat or lon:
        raise WeatherError("Incomplete location in environment variables")
    return None


def _location_from_config() -> Optional[Tuple[float, float]]:
    """Return coordinates from the configuration file if both are defined.

    The configuration is loaded on each call. If loading fails a
    ``WeatherError`` is raised with the message from ``load_config``.

    When only one of the latitude or longitude values exists, a
    ``WeatherError`` is raised. When neither is found the function
    returns ``None``.
    """
    try:
        cfg = load_config()
    except ValueError as exc:
        raise WeatherError(str(exc)) from exc

    if cfg.lat is None and cfg.lon is None:
        return None
    if cfg.lat is None or cfg.lon is None:
        raise WeatherError("Incomplete location in configuration file")
    return cfg.lat, cfg.lon


def _location_from_termux() -> Tuple[float, float]:
    """Retrieve GPS coordinates using ``termux-location``.

    A `WeatherError` is raised when the command fails or returns
    malformed data. Successful calls return a tuple of latitude and
    longitude.
    """
    result = subprocess.run(
        [
            "termux-location",
            "-p",
            "gps",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout:
        raise WeatherError("Failed to obtain location from termux")
    try:
        data = json.loads(result.stdout)
        return round(float(data["latitude"]), 4), round(float(data["longitude"]), 4)
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise WeatherError("Invalid location data from termux") from exc


def resolve_location(
    lat: Optional[float],
    lon: Optional[float],
    city: Optional[str],
    token: str,
) -> Tuple[float, float]:
    """Resolve the desired location following the configured priority."""
    if lat is not None or lon is not None:
        if lat is None or lon is None:
            raise WeatherError("Both latitude and longitude must be provided")
        return lat, lon

    if city:
        return _geocode_city(city, token)

    env_loc = _location_from_env()
    if env_loc:
        return env_loc

    cfg_loc = _location_from_config()
    if cfg_loc:
        return cfg_loc

    if os.environ.get("PREFIX") == "/data/data/com.termux/files/usr":
        return _location_from_termux()

    raise WeatherError("Unable to determine location")


__all__ = [
    "resolve_location",
]
