# Weather

A simple command-line utility for fetching weather information from [OpenWeatherMap](https://openweathermap.org/).

The script determines your location automatically and caches results to avoid unnecessary API calls.

## Requirements

- Python 3.10+
- An OpenWeatherMap API token provided via the `OWM_TOKEN` environment variable
  or a `.env` file containing a line like `OWM_TOKEN=your-token`

## Installation

Recommended: install with [pipx](https://pipx.pypa.io/) so the `weather` command
is isolated and on your PATH:

```bash
pipx install .
```

Updating after changes during development:

```bash
pipx reinstall .
```

Alternatives:

```bash
# User install (places script in ~/.local/bin)
pip install --user .

# Or inside a virtualenv
pip install .
```

## Usage

Run the CLI:

```bash
weather [OPTIONS]
```

### Options

- `-u, --units [metric|imperial|standard]` — Units for the output. Defaults to `metric`.
- `-f, --force` — Force an update by ignoring cached data.
- `--lat, --latitude FLOAT` — Latitude of the target location. Must be used with `--lon`.
- `--lon, --longitude FLOAT` — Longitude of the target location. Must be used with `--lat`.
- `-c, --city TEXT` — Name of the target city. Cannot be used with `--lat` or `--lon`.
- `--token TEXT` — OpenWeatherMap API token (overrides env and .env).
- `-v, --verbose` — Print progress information to stderr.
- `-s, --silent` / `-q, --quiet` — Suppress normal output.
- `--cache-max-range NUMBER` — Define max distance in meters of cache.
- `--cache-max-age NUMBER` — Define max age in seconds of cache.

### Location Resolution

If latitude and longitude are not supplied, the tool resolves the location in the following order:

1. `$LATITUDE` and `$LONGITUDE` environment variables.
2. `~/.config/weather.conf` configuration file.
3. `termux-location` when running inside Termux.

### Configuration File

The preferred location is XDG-style: `~/.config/weather/weather.conf`. The tool
also accepts `~/.config/weather.conf` for backward compatibility.

You can include settings like:

```
LAT=39.7533
LONGITUDE=-105.00047
UNITS=imperial
CACHE_MAX_RANGE=1500
CACHE_MAX_AGE=600
OWM_TOKEN=your-token-here
```

### Caching

Responses are stored as JSON in `~/.cache/weather.json` (or `$STORAGE/.cache/weather.json` when `$STORAGE` is writable). Cached data younger than the configured `cache-max-age` is reused and only when within `cache-max-range` meters of the target location. Use `--force` to bypass the cache.

- To disable the distance check entirely, set `--cache-max-range -1`.

## Example

```bash
OWM_TOKEN=your-token weather -c "Denver" --units imperial
# or set OWM_TOKEN in a .env file and simply run:
weather -c "Denver" --units imperial
```

A single line of JSON describing the current weather will be printed to `stdout`.

## Development

Run [black](https://black.readthedocs.io/) in check mode to verify formatting:

```bash
black --check .
```

Run tests with pytest (optional):

```bash
pytest -q
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
