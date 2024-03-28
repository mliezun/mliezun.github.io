#!/bin/bash

set -euo pipefail

./scripts/download_grotsky_binary.sh

exec watchmedo auto-restart -d . -p "*.gr;*.css;*.md" --recursive --signal SIGKILL \
    -- ./.grotsky/grotsky src/main.gr
