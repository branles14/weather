# Weather

A simple command-line utility for fetching weather information from [OpenWeatherMap](https://openweathermap.org/).

The script determines your location automatically and caches results to avoid unnecessary API calls.

## Requirements

- Python 3.10+
- An OpenWeatherMap API token provided via the `OWM_TOKEN` environment variable
- `click` (installable with `pip`)

## Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the CLI:

```bash
python -m weather.cli [OPTIONS]
```

### Options

- `-u, --units [metric|imperial|standard]` — Units for the output. Defaults to `metric`.
- `-f, --force` — Force an update by ignoring cached data.
- `--lat, --latitude FLOAT` — Latitude of the target location. Must be used with `--lon`.
- `--lon, --longitude FLOAT` — Longitude of the target location. Must be used with `--lat`.
- `-c, --city TEXT` — Name of the target city. Cannot be used with `--lat` or `--lon`.
- `-v, --verbose` — Print progress information to stderr.
- `-s, --silent` — Suppress normal output.
- `--cache-max-range NUMBER` — Define max distance in meters of cache.
- `--cache-max-age NUMBER` — Define max age in seconds of cache.

### Location Resolution

If latitude and longitude are not supplied, the tool resolves the location in the following order:

1. `$LATITUDE` and `$LONGITUDE` environment variables.
2. `~/.config/weather.conf` configuration file.
3. `termux-location` when running inside Termux.

### Configuration File

`~/.config/weather.conf` may contain lines such as:

```
LAT=39.7533
LONGITUDE=-105.00047
UNITS=imperial
CACHE_MAX_RANGE=1500
CACHE_MAX_AGE=600
```

### Caching

Responses are stored as JSON in `~/.cache/weather.json` (or `$STORAGE/.cache/weather.json` when `$STORAGE` is writable). Cached data younger than the configured `cache-max-age` is reused and only when within `cache-max-range` meters of the target location. Use `--force` to bypass the cache.

## Example

```bash
OWM_TOKEN=your-token python -m weather.cli -c "Denver" --units imperial
```

A single line of JSON describing the current weather will be printed to `stdout`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
