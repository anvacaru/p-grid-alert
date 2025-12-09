# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${PROJECT_DIR}/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/run_${TIMESTAMP}.log"

echo $PROJECT_DIR
echo $LOG_DIR
echo $TIMESTAMP
echo $LOG_FILE

# Create log directory if it doesn't exist
mkdir -p "${LOG_DIR}"

# Change to project directory
cd "${PROJECT_DIR}" || exit 1

# Run with verbose logging, redirect output to log file
uv run p-grid-alert --verbose >> "${LOG_FILE}" 2>&1

echo "Completed at $(date)" >> "${LOG_FILE}"