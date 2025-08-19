"""Command line interface for the weather utility."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click

from .config import load_config
from .env import ensure_owm_token
from .core import WeatherError
from .core.location import resolve_location
from .core.update import (
    DEFAULT_MAX_AGE,
    DEFAULT_MAX_RANGE,
    cache_file,
    fetch_weather,
    read_cache,
)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-u",
    "--units",
    default=None,
    show_default="from config or 'metric'",
    type=click.Choice(["metric", "imperial", "standard"], case_sensitive=False),
)
@click.option(
    "-f", "--force", is_flag=True, help="Force update by bypassing data age check"
)
@click.option("--lat", "--latitude", "lat", type=float)
@click.option("--lon", "--longitude", "lon", type=float)
@click.option("-c", "--city", type=str, help="City name for the target location")
@click.option("--token", type=str, default=None, help="OpenWeatherMap API token")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option(
    "-s",
    "--silent",
    "-q",
    "--quiet",
    is_flag=True,
    help="Suppress normal output",
)
@click.option(
    "--cache-max-range",
    default=None,
    show_default="from config or %d" % DEFAULT_MAX_RANGE,
    type=int,
    help="Define max distance in meters of cache",
)
@click.option(
    "--cache-max-age",
    default=None,
    show_default="from config or %d" % DEFAULT_MAX_AGE,
    type=int,
    help="Define max age in seconds of cache",
)
def main(
    units: str | None,
    force: bool,
    lat: float | None,
    lon: float | None,
    city: str | None,
    token: str | None,
    verbose: bool,
    silent: bool,
    cache_max_range: int | None,
    cache_max_age: int | None,
) -> None:
    """Retrieve and display weather data from OpenWeatherMap."""

    try:
        config = load_config()
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if units is None:
        units = config.units or "metric"
    if cache_max_range is None:
        cache_max_range = config.cache_max_range or DEFAULT_MAX_RANGE
    if cache_max_age is None:
        cache_max_age = config.cache_max_age or DEFAULT_MAX_AGE

    if not token:
        try:
            token = ensure_owm_token()
        except WeatherError as exc:
            raise click.ClickException(str(exc)) from exc

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
