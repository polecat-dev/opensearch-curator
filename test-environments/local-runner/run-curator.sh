#!/bin/bash
# OpenSearch Curator - WSL Helper Script
# Makes it easier to run curator commands from WSL

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/../.." && pwd )"
CURATOR="${REPO_ROOT}/.venv-wsl/bin/curator"
CONFIG="${SCRIPT_DIR}/curator.yml"

# Check if curator is installed
if [ ! -f "$CURATOR" ]; then
    echo "Error: Curator not found at $CURATOR"
    echo "Please install it first: cd \"$REPO_ROOT\" && .venv-wsl/bin/pip install -e ."
    exit 1
fi

# Check if config exists
if [ ! -f "$CONFIG" ]; then
    echo "Error: Config file not found at $CONFIG"
    exit 1
fi

# If no arguments, show usage
if [ $# -eq 0 ]; then
    echo "Usage: $0 <action-file> [--dry-run]"
    echo ""
    echo "Available action files:"
    ls -1 "${SCRIPT_DIR}"/*.yml 2>/dev/null | grep -v curator.yml | xargs -n1 basename
    echo ""
    echo "Examples:"
    echo "  $0 01-list-all-indices.yml --dry-run"
    echo "  $0 02-delete-old-test-indices.yml --dry-run"
    exit 0
fi

# Run curator with the specified action file
ACTION_FILE="$1"
shift  # Remove first argument so $@ contains remaining args

# If action file doesn't have path, assume it's in current directory
if [ ! -f "$ACTION_FILE" ]; then
    ACTION_FILE="${SCRIPT_DIR}/${ACTION_FILE}"
fi

if [ ! -f "$ACTION_FILE" ]; then
    echo "Error: Action file not found: $ACTION_FILE"
    exit 1
fi

echo "Running curator..."
echo "  Config: $CONFIG"
echo "  Action: $(basename $ACTION_FILE)"
echo "  Args: $@"
echo ""

"$CURATOR" --config "$CONFIG" "$ACTION_FILE" "$@"
