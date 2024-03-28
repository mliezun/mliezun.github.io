#!/bin/bash

set -euo pipefail

./scripts/download_grotsky_binary.sh

exec watchmedo auto-restart -d . -p "*" --recursive \
    -- ./.grotsky/grotsky src/main.gr
