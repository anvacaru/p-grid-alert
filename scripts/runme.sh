#!/usr/bin/env bash
set -euo pipefail

# cron starts with a minimal PATH; uv's default install location is ~/.local/bin.
export PATH="${HOME}/.local/bin:${PATH}"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${PROJECT_DIR}/logs"
LOG_FILE="${LOG_DIR}/run_$(date +"%Y%m%d_%H%M%S").log"

mkdir -p "${LOG_DIR}"
cd "${PROJECT_DIR}"

status=0
uv run p-grid-alert --verbose >>"${LOG_FILE}" 2>&1 || status=$?

echo "Finished at $(date) with exit code ${status}" >>"${LOG_FILE}"
exit "${status}"
