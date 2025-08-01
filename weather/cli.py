"""Command line interface for the weather utility."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click

from .config import load_config
from .core import WeatherError
from .core.location import resolve_location
from .core.update import (
    DEFAULT_MAX_AGE,
    DEFAULT_MAX_RANGE,
    cache_file,
    fetch_weather,
    read_cache,
)

CONFIG = load_config()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-u",
    "--units",
    default=CONFIG.units or "metric",
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
@click.option(
    "--cache-max-range",
    default=CONFIG.cache_max_range or DEFAULT_MAX_RANGE,
    show_default=True,
    type=int,
    help="Define max distance in meters of cache",
)
@click.option(
    "--cache-max-age",
    default=CONFIG.cache_max_age or DEFAULT_MAX_AGE,
    show_default=True,
    type=int,
    help="Define max age in seconds of cache",
)
def main(
    units: str,
    force: bool,
    lat: float | None,
    lon: float | None,
    city: str | None,
    verbose: bool,
    silent: bool,
    cache_max_range: int,
    cache_max_age: int,
) -> None:
    """Retrieve and display weather data from OpenWeatherMap."""

    token = os.environ.get("OWM_TOKEN")
    if not token:
        env_path = Path(__file__).resolve().parent.parent / ".env"
        if env_path.is_file():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("TOKEN="):
                    token = line.split("=", 1)[1].strip()
                    break
    if not token:
        raise click.ClickException("No OpenWeatherMap token found in OWM_TOKEN or .env")

    if city and (lat is not None or lon is not None):
        raise click.BadOptionUsage(
            "--city", "--city cannot be used with --latitude/--longitude"
        )

    try:
        lat, lon = resolve_location(lat, lon, city, token)
    except WeatherError as exc:
        raise click.ClickException(str(exc)) from exc

    cfile = cache_file()

    data = (
        None if force else read_cache(cfile, lat, lon, cache_max_range, cache_max_age)
    )
    if data is None:
        try:
            data = fetch_weather(lat, lon, units, token, cfile, verbose)
        except WeatherError as exc:
            raise click.ClickException(str(exc)) from exc

    if not silent:
        json.dump(data, sys.stdout)
        sys.stdout.write("\n")
