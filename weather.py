#!/usr/bin/env python3
"""Simple weather utility implemented in Python.

This script retrieves weather data from the OpenWeatherMap API using
`termux-location` to determine the current location. Results are cached
in a JSON file in ``~/.cache`` to avoid unnecessary network requests.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


DEFAULT_CACHE_DIR = Path.home() / ".cache"
DEFAULT_CACHE_FILE = DEFAULT_CACHE_DIR / "weather.json"
DEFAULT_MAX_AGE = 300  # seconds


class WeatherError(Exception):
    """Custom exception for weather errors."""


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Retrieve weather data")
    parser.add_argument("--unit", choices=["metric", "imperial", "standard"], default="metric",
                        help="Units for temperature")
    parser.add_argument("--force", action="store_true", help="Force update weather data")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--silent", action="store_true", help="Suppress normal output")
    return parser.parse_args()


def get_location() -> tuple[float, float]:
    """Return the current latitude and longitude using ``termux-location``."""
    result = subprocess.run(["termux-location", "-r", "last"], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout:
        raise WeatherError("Failed to obtain location from termux")

    try:
        data = json.loads(result.stdout)
        lat = round(float(data["latitude"]), 4)
        lon = round(float(data["longitude"]), 4)
        return lat, lon
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise WeatherError("Invalid location data") from exc


def read_cache(cache_file: Path, max_age: int) -> dict | None:
    """Return cached weather data if it exists and is recent."""
    if not cache_file.is_file():
        return None

    with cache_file.open("r", encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError:
            return None

    dt = data.get("current", {}).get("dt")
    if not isinstance(dt, (int, float)):
        return None

    if time.time() - dt > max_age:
        return None
    return data


def update_weather(lat: float, lon: float, units: str, token: str, cache_file: Path, verbose: bool) -> dict:
    """Fetch weather data from the API and store it in ``cache_file``."""
    url = (
        "https://api.openweathermap.org/data/3.0/onecall"
        f"?lat={lat}&lon={lon}&appid={token}&units={units}"
    )
    if verbose:
        print("Requesting data from OpenWeatherMap", file=sys.stderr)

    try:
        with urlopen(url) as resp:
            data = json.load(resp)
    except URLError as exc:
        raise WeatherError("Failed to retrieve weather data") from exc

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with cache_file.open("w", encoding="utf-8") as fh:
        json.dump(data, fh)

    return data


def main() -> int:
    args = parse_arguments()
    token = os.environ.get("OWM_TOKEN")
    if not token:
        print("Error: OWM_TOKEN environment variable not set", file=sys.stderr)
        return 1

    try:
        lat, lon = get_location()
    except WeatherError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    data = read_cache(DEFAULT_CACHE_FILE, DEFAULT_MAX_AGE)
    if data is None or args.force:
        try:
            data = update_weather(lat, lon, args.unit, token, DEFAULT_CACHE_FILE, args.verbose)
        except WeatherError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    if not args.silent:
        json.dump(data, sys.stdout)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
