# Weather

A simple python based weather utility for managing OpenWeatherMap data.

## Instructions

- Follow Python's best practices.
- Keep code clean, modular and manageable.
- Always keep `README.md` and `requirements.txt` up-to-date.
- Use click to handle the cli.
- Test with black.

## Notes

### Arguments

The utility should accept the following arguments:

- `-h|--help` — Display help message
- `-u|--units` — Set units, either: metric, imperial, standard. (Default: metric)
- `-f|--force` — Force update by bypassing data age check. (Disabled by default)
- `--lat|--latitude LATITUDE` — Provide the latitude of the target location. Must be used with `--lon|--longitude`.
- `--lon|--longitude LONGITUDE` — Provide the longitude of the target location. Must be used with `--lat|--latitude`.
- `-c|--city CITY` — Provide the name of the target location. Cannot be used with `--lat|--latitude` or `--lon|--longitude`.
- `--cache-max-range` — Define max distance in meteres of cache.
- `--cache-max-age` — Define max age in seconds of cache.

### Location Resolution Priority

The system determines location using the following prioritized sources. Each step must provide both latitude and longitude to be considered valid:

1. Command-line Arguments: If `--lat|--latitude` and `--lon|--longitude` are both provided, use these values. If only one is provided, exit with an error indicating incomplete location input.
2. Environment Variables: If both `$LATITUDE` and `$LONGITUDE` are set, use these values. If only one is set, exit with an error that clearly identifies this as the cause.
3. Configuration File: If `~/.config/weather.conf` exists, parse it as a dotenv-style file to extract `LAT` and `LON`. If both are found, use them. If only one is present, exit with an error that clearly identifies this as the cause.
4. System Utilities (Termux only): If no valid location has been found, and `$PREFIX` matches `/data/data/com.termux/files/usr`, attempt to retrieve GPS coordinates using `termux-location -p gps`

### Caching

Whenever the utility gets new weather data from the OpenWeatherMap API, it should save the data as a one-line json object.

#### Cache File

If `$STORAGE` is set, is a directory and can be written inside of, then `cache_file` = `$STORAGE/.cache/weather.json`, otherwise `cache_file` = `$HOME/.cache/weather.json`.
The utility should ensure the `.cache` directory exists as to avoid FileNotFoundError.

### Data Sourcing

#### Sourcing Data From Cache

If `cache_file` exists, can be read, and is a valid json object, then the utility should attempt to source `weather_data` from `cache_file`.

The cache is only considered valid if:

1. It's within `cache_max_range` meters of the target location.
2. It's less than `cache_max_age` seconds of the cache age.

### Output

The utility's standard output should be a one-line json print out of the OpenWeatherMap data.
