#!/bin/bash

set -euo pipefail

apt-get update -yyqq > /dev/null 2>&1

apt-get install -yyqq wget > /dev/null 2>&1

./scripts/start_dev_server.sh
