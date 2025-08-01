"""Command line interface for the weather utility."""

from __future__ import annotations

import json
import os
import sys

import click

from .config import load_config
from .core import WeatherError
from .core.location import resolve_location
from .core.update import (
    DEFAULT_MAX_AGE,
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

    cfile = cache_file()

    data = None if force else read_cache(cfile, DEFAULT_MAX_AGE)
    if data is None:
        try:
            data = fetch_weather(lat, lon, units, token, cfile, verbose)
        except WeatherError as exc:
            raise click.ClickException(str(exc)) from exc

    if not silent:
        json.dump(data, sys.stdout)
        sys.stdout.write("\n")
