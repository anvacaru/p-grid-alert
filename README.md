# Power Grid Alert

Automated monitoring tool for scheduled power outages.
Checks weekly PDF documents and sends email alerts when outages are detected for a specified street.

## Dependencies

- **Python**: 3.10+
- **uv**: Package manager ([installation guide](https://github.com/astral-sh/uv))
- **make**: Build automation (optional, for development)

## Installation
```bash
# Install dependencies
uv sync
```

## Usage

#### Run manually
```bash
# Basic run
uv run p-grid-alert
```

#### Automated daily execution

The project includes a script for daily automated runs at 10 PM:
```bash
# Make script executable
chmod +x scripts/run_daily.sh

# Add to crontab
crontab -e
# Add: 0 22 * * * /path/to/p-grid-alert/scripts/run_daily.sh
```

Logs are saved to `logs/run_YYYYMMDD_HHMMSS.log`

## Development
```bash
# Format code
make format

# Run checks (linting, type checking)
make check

# Run tests
make test-unit
```

## How it works

1. Fetches weekly PDF schedules from the power grid website.
2. Extracts text and searches for your street name.
3. Parses outage date and time.
4. Sends an email alert if there are any future outages.