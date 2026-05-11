#!/bin/bash
# Thin wrapper: loads config and runs the Python generator (hvcc or libpd).
# Requires Python 3.8+ (stdlib only). Use LF line endings on Unix.
#
# Usage: ./setup_env_with_hvcc.sh -c config_template.json

set -euo pipefail

while getopts "c:" opt; do
  case $opt in
    c) CONFIG_FILE="$OPTARG" ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
  esac
done

if [ -z "${CONFIG_FILE:-}" ]; then
  echo "Usage: $0 -c <config_file.json>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

exec python3 tools/generate.py -c "$CONFIG_FILE"
