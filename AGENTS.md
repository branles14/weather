# Weather

A simple python based weather utility for managing OpenWeatherMap data.

## Arguments

The script should accept the following arguments:

- `-h|--help`
- `-u|--units`
- `-f|--force`
- `--lat|--latitude`
- `--lon|--longitude`
- `-c|--city`

## Location Resolution Priority

The system determines location using the following prioritized sources. Each step must provide both latitude and longitude to be considered valid:

1. Command-line Arguments: If `--lat|--latitude` and `--lon|--longitude` are both provided, use these values. If only one is provided, exit with an error indicating incomplete location input.
2. Environment Variables: If both `$LATITUDE` and `$LONGITUDE` are set, use these values. If only one is set, exit with an error that clearly identifies this as the cause.
3. Configuration File: If `~/.config/weather.conf` exists, parse it as a dotenv-style file to extract `LAT` and `LON`. If both are found, use them. If only one is present, exit with an error that clearly identifies this as the cause.
4. System Utilities (Termux only): If no valid location has been found, and `$PREFIX` matches `/data/data/com.termux/files/usr`, attempt to retrieve GPS coordinates using `termux-location -p gps`
