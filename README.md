# Weather

A simple command-line utility for fetching weather information from [OpenWeatherMap](https://openweathermap.org/).

The script determines your location automatically and caches results to avoid unnecessary API calls.

## Requirements

- Python 3.10+
- An OpenWeatherMap API token provided via the `OWM_TOKEN` environment variable
  or a `.env` file containing a line like `OWM_TOKEN=your-token`

## Installation

You have a few options depending on your environment and preference.

### Termux (recommended)

Termux does not always provide `pipx`. The most reliable approach is to install
into the repo’s virtualenv (managed by `.envrc`/direnv) and create a small
wrapper in `~/.local/bin` that runs the CLI via that venv.

1) In the repo, set up the venv and install:

```bash
direnv allow           # once, to permit activation of .venv
pip install -e .       # or: pip install -e .[dev]
```

2) Create the wrapper script at `~/.local/bin/weather`:

```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/weather <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
REPO="$HOME/Repos/weather"          # adjust if your repo path differs
VENV="$REPO/.venv"
PY="$VENV/bin/python"
if [ ! -x "$PY" ]; then
  echo "weather: venv not found at $VENV. Run: (cd $REPO && direnv allow && pip install -e .)" >&2
  exit 1
fi
exec "$PY" -m weather.cli "$@"
EOF
chmod +x ~/.local/bin/weather
```

3) Ensure `~/.local/bin` is on your PATH and test:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.profile
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
exec $SHELL -l
weather -h
```

Alternative: instead of a wrapper, you can symlink the venv entrypoint from the
repo directory:

```bash
mkdir -p ~/.local/bin
ln -sf "$(pwd)/.venv/bin/weather" ~/.local/bin/weather
```

Both approaches avoid recursion and ensure the command uses this project’s
virtualenv. If you later move the repo, update the wrapper’s `REPO` path or
recreate the symlink.

### Termux + direnv (repo venv only)

This repository includes an `.envrc` that auto-creates and activates a
virtualenv in `.venv` (via `direnv`). Inside the repo:

```bash
direnv allow     # once, to permit activation
pip install -e . # or `pip install -e .[dev]` for dev tools
weather -h       # available while you are in the repo (venv active)
```

Note: `weather` is only on PATH while the venv is active (i.e., when you are in
the repo). Use the Termux wrapper above for a global command.

### Global install with pipx (recommended)

Install with [pipx](https://pipx.pypa.io/) to get an isolated environment and a
`weather` command on your PATH everywhere:

```bash
# On systems where pipx is available
# (Termux may not ship pipx; prefer the Termux method above)
python -m pip install --user pipx  # or your OS package manager
pipx ensurepath         # ensure ~/.local/bin is on PATH
pipx install .          # from the repo directory

# Update after changes
pipx reinstall .
```

### Global install with pip --user

If you prefer a user install:

```bash
# Temporarily avoid the repo venv if direnv is active
direnv disable  # or run from a parent directory
python -m pip install --user .

# Ensure user bin is on PATH (Termux)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.profile
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Plain virtualenv (no direnv)

```bash
python -m venv ~/.virtualenvs/weather
source ~/.virtualenvs/weather/bin/activate
pip install .
weather -h
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

1. CLI `--lat/--lon` options (both required if used).
2. `$LATITUDE` and `$LONGITUDE` environment variables (both must be set).
3. XDG config file `~/.config/weather/weather.conf` (also accepts legacy
   `~/.config/weather.conf`), using keys `LAT|LATITUDE` and `LON|LONGITUDE`.
4. `termux-location -p gps` when running inside Termux.

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
