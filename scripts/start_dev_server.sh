#!/bin/bash

set -euo pipefail

./scripts/download_grotsky_binary.sh

exec watchmedo auto-restart -d . -p "*" -i ".git;.vscode" --recursive --signal SIGKILL \
    -- ./.grotsky/grotsky src/main.gr
