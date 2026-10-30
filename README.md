# Power Grid Alert

Automated monitoring tool for scheduled power outages.
Checks weekly PDF documents and sends email alerts when outages are detected for a specified street.

## Dependencies

- **Python**: 3.13+
- **uv**: Package manager ([installation guide](https://github.com/astral-sh/uv))
- **make**: Build automation (optional, for development)

## Installation
```bash
# Install dependencies
uv sync
```

## Configuration

All settings are required and are read from the environment or from a `.env` file in the project root.

| Variable               | Meaning                                                  |
|------------------------|----------------------------------------------------------|
| `P_GRID_TARGET_URL`    | Page that links the weekly outage PDFs                   |
| `P_GRID_TARGET_DOMAIN` | Host the PDF links must point to                         |
| `P_GRID_STREET`        | Street to look for (case and diacritics are ignored)     |
| `P_GRID_EMAIL_TO`      | Comma-separated recipient addresses                      |
| `P_GRID_SMTP_SERVER`   | SMTP host (STARTTLS is used)                             |
| `P_GRID_SMTP_PORT`     | SMTP port                                                |
| `P_GRID_SMTP_USER`     | SMTP login, also used as the sender address              |
| `P_GRID_SMTP_PASS`     | SMTP password                                            |

## Usage

#### Run manually
```bash
# Basic run
uv run p-grid-alert
```

#### Automated daily execution

The project includes a script for daily automated runs at 10 PM:
```bash
# Add to crontab
crontab -e
# Add: 0 22 * * * /path/to/p-grid-alert/scripts/runme.sh
```

Logs are saved to `logs/run_YYYYMMDD_HHMMSS.log`.
The script expects `uv` in `~/.local/bin` (its default install location) or on cron's `PATH`.
The run exits non-zero if any document could not be processed or an alert could not be sent.

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