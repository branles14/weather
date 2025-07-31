# weather

A simple weather utility powered by Python. It fetches weather data from
[OpenWeatherMap](https://openweathermap.org/) using your current location
reported by `termux-location`. Results are cached in `~/.cache/weather.json`
for quick subsequent access.

## Usage

```bash
./weather.py [--unit metric|imperial|standard] [--force] [--verbose] [--silent]
```

Set the `OWM_TOKEN` environment variable to your OpenWeatherMap API token
before running the script.
