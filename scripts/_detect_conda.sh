#!/bin/bash
# Shared helper: detect whether conda or mamba can run the totp environment.
# Source this file from other scripts. It sets CONDA_COMMAND and CONDA_ENV.

CONDA_ENV='totp'

_can_run_env() {
    "$1" run -n "$CONDA_ENV" --no-capture-output python -c '' 2>/dev/null
}

CONDA_COMMAND=""
for cmd in conda mamba; do
    if command -v -- "$cmd" > /dev/null 2>&1 && _can_run_env "$cmd"; then
        CONDA_COMMAND="$cmd"
        break
    fi
done

if [ -z "$CONDA_COMMAND" ]; then
    echo "Error: Could not run the '$CONDA_ENV' environment with either conda or mamba."
    echo "Make sure the environment exists (conda env create -f environment.yml) and try again."
    exit 1
fi
