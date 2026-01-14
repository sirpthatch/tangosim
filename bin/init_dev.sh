#!/bin/sh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

export PYTHONPATH="$SCRIPT_DIR/../src:./src:$PYTHONPATH"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
