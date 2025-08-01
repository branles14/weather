"""Command line interface for the weather utility."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import click

DEFAULT_MAX_AGE = 300


class WeatherError(Exception):
    """Custom exception for weather errors."""


def _cache_file() -> Path:
    storage = os.environ.get("STORAGE")
    base = (
        Path(storage)
        if storage and os.path.isdir(storage) and os.access(storage, os.W_OK)
        else Path.home()
    )
    cache_dir = base / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "weather.json"


def _read_cache(cache_file: Path, max_age: int) -> dict | None:
    if not cache_file.is_file():
        return None
    try:
        with cache_file.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError:
        return None

    dt = data.get("current", {}).get("dt")
    if not isinstance(dt, (int, float)):
        return None
    if time.time() - dt > max_age:
        return None
    return data


def _fetch_weather(
    lat: float, lon: float, units: str, token: str, cache_file: Path, verbose: bool
) -> dict:
    url = (
        "https://api.openweathermap.org/data/3.0/onecall"
        f"?lat={lat}&lon={lon}&appid={token}&units={units}"
    )
    if verbose:
        click.echo("Requesting data from OpenWeatherMap", err=True)
    try:
        with urlopen(url) as resp:
            data = json.load(resp)
    except URLError as exc:
        raise WeatherError("Failed to retrieve weather data") from exc

    with cache_file.open("w", encoding="utf-8") as fh:
        json.dump(data, fh)
    return data


def _geocode_city(city: str, token: str) -> tuple[float, float]:
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


def _location_from_env() -> tuple[float, float] | None:
    lat = os.environ.get("LATITUDE")
    lon = os.environ.get("LONGITUDE")
    if lat and lon:
        return float(lat), float(lon)
    if lat or lon:
        raise WeatherError("Incomplete location in environment variables")
    return None


def _location_from_config() -> tuple[float, float] | None:
    cfg = Path.home() / ".config/weather.conf"
    if not cfg.is_file():
        return None
    lat = lon = None
    for line in cfg.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().upper()
        value = value.strip()
        if key == "LAT":
            lat = float(value)
        elif key == "LON":
            lon = float(value)
    if lat is not None and lon is not None:
        return lat, lon
    if lat is not None or lon is not None:
        raise WeatherError("Incomplete location in configuration file")
    return None


def _location_from_termux() -> tuple[float, float]:
    result = subprocess.run(
        ["termux-location", "-p", "gps"], capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout:
        raise WeatherError("Failed to obtain location from termux")
    try:
        data = json.loads(result.stdout)
        return round(float(data["latitude"]), 4), round(float(data["longitude"]), 4)
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise WeatherError("Invalid location data from termux") from exc


def resolve_location(
    lat: float | None, lon: float | None, city: str | None, token: str
) -> tuple[float, float]:
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


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-u",
    "--units",
    default="metric",
    show_default=True,
    type=click.Choice(["metric", "imperial", "standard"], case_sensitive=False),
)
@click.option(
    "-f", "--force", is_flag=True, help="Force update by bypassing data age check"
)
@click.option("--lat", "--latitude", "lat", type=float)
@click.option("--lon", "--longitude", "lon", type=float)
@click.option("-c", "--city", type=str, help="City name for the target location")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option("-s", "--silent", is_flag=True, help="Suppress normal output")
def main(
    units: str,
    force: bool,
    lat: float | None,
    lon: float | None,
    city: str | None,
    verbose: bool,
    silent: bool,
) -> None:
    """Retrieve and display weather data from OpenWeatherMap."""

    token = os.environ.get("OWM_TOKEN")
    if not token:
        raise click.ClickException("OWM_TOKEN environment variable not set")

    try:
        lat, lon = resolve_location(lat, lon, city, token)
    except WeatherError as exc:
        raise click.ClickException(str(exc)) from exc

    cache_file = _cache_file()

    data = None if force else _read_cache(cache_file, DEFAULT_MAX_AGE)
    if data is None:
        try:
            data = _fetch_weather(lat, lon, units, token, cache_file, verbose)
        except WeatherError as exc:
            raise click.ClickException(str(exc)) from exc

    if not silent:
        json.dump(data, sys.stdout)
        sys.stdout.write("\n")
