#!/bin/zsh
cache_dir="${HOME}/.cache"
cache_file="${cache_dir}/weather.json"

# Default settings
units="metric"
location="current"
force_update=0
max_data_age=300
verbose=0
silent=0

# Function to display help message
function print_usage {
    cat <<- EOF

Usage: weather [options]

Options:
  -h, --help                Display this help message.
  --unit <unit>             Set units (metric, imperial, standard).
  --force                   Force update weather data.
  --verbose                 Enable verbose mode.
  --silent                  Update silently.

Example:
  weather --unit metric
  weather --unit imperial --force

EOF
}

# Function to print error message
function error {
    local message="${1:-Unknown error}"
    local color="${COLOR_RED:-#ff0000}"

    print -P "%B%F{$color}Error%f:%b $message" >&2
}

# Function to check for errors
function error_check {
    local required_pkgs=("bc" "curl" "jq")
    local missing_pkgs=()

    # Check for missing packages
    for pkg in "${required_pkgs[@]}"; do
        if ! command -v "$pkg" &>/dev/null; then
            missing_pkgs+=("$pkg")
        fi
    done

    # Display error if missing packages
    if [[ "${#missing_pkgs[@]}" -gt 0 ]]; then
        error "Missing packages: ${missing_pkgs[*]}"
        return 1
    fi

    # Ensure 'OWM_TOKEN' is set
    if [[ -z "$OWM_TOKEN" ]]; then
        error "Undefined variable: OWM_TOKEN"
        return 1
    fi

    # Ensure cache_dir exists
    if [[ -n "$cache_dir" ]]; then
        mkdir -p "$cache_dir"
    else
        error "Undefined variable: cache_dir"
        return 1
    fi
}

# Function to parse arguments
function parse_arguments {
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -h|--help|--help-all|-help|help)
                print_usage
                exit 0
                ;;
            --unit)
                if [[ -n "$2" && "$2" != -* ]]; then
                    case "$2" in
                        Metric|metric|C|c)
                            units="metric"
                            ;;
                        Imperial|imperial|Fahrenheit|fahrenheit|F|f)
                            units="imperial"
                            ;;
                        Standard|standard)
                            units="standard"
                            ;;
                        *)
                            error "Unsupported value for --unit: $2"
                            exit 1
                            ;;
                    esac
                    shift
                else
                    error "Missing argument for --unit"
                    print_usage
                    exit 1
                fi
                ;;
            --force)
                force_update=1
                ;;
            --verbose)
                verbose=1
                ;;
            --silent)
                silent=1
                ;;
            -*)
                error "Unknown option: $1"
                print_usage
                exit 1
                ;;
            *)
                error "Unknown argument: $1"
                print_usage
                exit 1
                ;;
        esac
        shift
    done
}

# Function to get location
function get_location {  
    local loc_data  
    if [[ "$location" == "current" ]]; then  
        loc_data=$(termux-location -r last)  
        if [[ "$?" -eq 0 && -n "$loc_data" ]]; then  
            # Extract latitude and longitude  
            lat=$(jq -r '.latitude' <<< "$loc_data")  
            lon=$(jq -r '.longitude' <<< "$loc_data")  
            # Shorten to 4 decimals  
            lat=$(printf "%.4f" "$lat")  
            lon=$(printf "%.4f" "$lon")  
            if [[ -n "$lat" && -n "$lon" ]]; then  
                return 0  
            fi  
        fi  
    else  
        error "City names not yet supported"  
        return 1  
    fi  
  
    error "Failed to determine location"  
    return 1  
}  

# Function to read weather data from cache
function read_cache {
    local data_age dt

    # Ensure 'cache_file' exists
    if [[ ! -f "$cache_file" ]]; then
        return 1
    fi

    weather_data=$(cat "$cache_file")

    # Check data age
    dt=$(jq -c '.current.dt' <<< "$weather_data")
    data_age=$(($(date -u +%s)-$dt))
    if [[ "$data_age" -gt "$max_data_age" ]]; then
        return 2
    fi

}

# Function to update weather data
function update_weather_data {
    local url="https://api.openweathermap.org/data/3.0/onecall"
    url="${url}?lat=${lat}&lon=${lon}&appid=${OWM_TOKEN}"
    url="${url}&units=${units:-metric}"

    # Announce request
    if [[ "$verbose" -eq 1 ]]; then
        print "Requesting data from Openweathermap"
    fi

    # Send request
    curl -s -f "$url" -o "$cache_file"
    if [[ "$?" -ne 0 ]]; then
        error "Failed to retrieve weather data"
        return 1
    fi
}

function main {
    # Parse arguments
    parse_arguments "$@"

    # Check for errors
    error_check || exit 1

    # Get current location
    get_location || exit 1

    # Get weather data
    read_cache
    if [[ "$?" -ne 0 || "$force_update" -ne 0 ]]; then
        update_weather_data || exit 1
        weather_data=$(<"$cache_file")
    fi

    # Print weather data
    if [[ "$silent" -eq 0 ]]; then
        echo -E "$weather_data"
    fi
}

main "$@"
