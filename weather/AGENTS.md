# weather/weather/

The source code directory of the utility.

## cli.py

The main entry point for the CLI where the command-line parser is defined.

## config.py

Handles configuration parsing from `~/.config/weather.conf`.

Here is an example configuration:

```
# Target Location
LAT=39.75330
LONGITUDE=-105.00047

# Settings
UNITS=metric
CACHE_MAX_RANGE=1500
CACHE_MAX_AGE=600
```
