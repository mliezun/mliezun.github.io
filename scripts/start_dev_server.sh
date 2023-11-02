#!/bin/bash

set -euo pipefail

./scripts/download_grotsky_binary.sh

./.grotsky/grotsky src/main.gr
