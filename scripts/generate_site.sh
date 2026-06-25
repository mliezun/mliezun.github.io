#!/bin/bash

./scripts/download_grotsky_binary.sh

./.grotsky/grotsky src/generate_site.gr

python3 ./scripts/fix_html_encoding.py

# Copy all files and folder from static to docs root
cp -r static/* docs/
