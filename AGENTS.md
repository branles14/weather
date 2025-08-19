# Weather

A simple python based weather utility for managing OpenWeatherMap data.

## Instructions

- Follow Python's best practices
- Keep code clean, modular and manageable
- Standardize variables naming convention
- Use detailed and informative docstrings
- Ensure errors are graceful and informative
- Keep `README.md` up-to-date
- Use click to handle the cli
- Test with black and pytest

## Notes

Use `find . -name AGENTS.md -print` to find all of the `AGENTS.md` files.
The rest of this document outlines details about the utility.

### Usage

After installing, the user can run the terminal command `weather` to get weather data.

### Arguments

The utility should accept the following arguments:

- `-h|--help` — Display help message
- `-u|--units` — Set units, either: metric, imperial, standard. (Default: metric)
- `-f|--force` — Force update by bypassing data age check. (Default: default)
- `--lat|--latitude FLOAT` — Provide the latitude of the target location. Must be used with `--lon|--longitude`
- `--lon|--longitude FLOAT` — Provide the longitude of the target location. Must be used with `--lat|--latitude`
- `-c|--city TEXT` — Provide the name of the target location. Cannot be used with `--lat|--latitude` or `--lon|--longitude`
- `--cache-max-range NUMBER` — Define max distance in meters of cache. (Default: 1000)
- `--cache-max-age NUMBER` — Define max age in seconds of cache. (Default: 300)
- `--token` — Provide the OpenWeatherMap API token (Default: unset)

### Location Resolution Priority

The system determines location using the following prioritized sources. Each step must provide both latitude and longitude to be considered valid:

1. Command-line Arguments: If `--lat|--latitude` and `--lon|--longitude` are both provided, use these values. If only one is provided, exit with an error indicating incomplete location input.
2. Environment Variables: If both `$LATITUDE` and `$LONGITUDE` are set, use these values. If only one is set, exit with an error that clearly identifies this as the cause.
3. Configuration File: Prefer XDG path `~/.config/weather/weather.conf` (also accepts legacy `~/.config/weather.conf`). Parse as dotenv-style and extract `LAT|LATITUDE` and `LON|LONGITUDE`. If both are found, use them. If only one is present, exit with an error that clearly identifies this as the cause.
4. System Utilities (Termux only): If no valid location has been found, and `$PREFIX` matches `/data/data/com.termux/files/usr`, attempt to retrieve GPS coordinates using `termux-location -p gps`

### Caching

Whenever the utility gets new weather data from the OpenWeatherMap API, it should save the data as a one-line json object.

#### Cache File

If `$STORAGE` is set, is a directory and can be written inside of, then `CACHE_FILE` = `$STORAGE/.cache/weather.json`, otherwise `CACHE_FILE` = `$HOME/.cache/weather.json`.
The utility should ensure the `.cache` directory exists as to avoid FileNotFoundError.

### Data Sourcing

Data should be sourced in this order to minimize API calls:

#### Sourcing Data From Cache

If `CACHE_FILE` exists, can be read, and is a valid json object, then the utility should attempt to source `WEATHER_DATA` from `CACHE_FILE`.

The cache is only considered valid if:

1. It's within `CACHE_MAX_RANGE` meters of the target location.
2. It's less than `CACHE_MAX_AGE` seconds of the cache age.

#### Sourcing Data From OpenWeatherMap

Use `$OWM_TOKEN` or `OWM_TOKEN` from `.env` in the project root to get the OpenWeatherMap API key.

### Output

The utility's standard output should be a one-line json print out of the OpenWeatherMap data.
