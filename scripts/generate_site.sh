#!/bin/bash

./scripts/download_grotsky_binary.sh

./.grotsky/grotsky src/generate_site.gr

# Copy all files and folder from static to docs root
cp -r static/* docs/
