#!/bin/bash

set -euo pipefail

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    ARCH="x86_64"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    ARCH="aarch64"
else
    echo "OS not supported."
    exit 1
fi

GROTSKY_VERSION=v0.0.20
GROTSKY_RELEASE=${GROTSKY_VERSION}

GROTSKY_FOLDER=.grotsky
GROTSKY_BINARY=$GROTSKY_FOLDER/grotsky
GROTSKY_TARGZ=grotsky-$GROTSKY_VERSION-$OS-$ARCH.tar.gz
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

build_patched_grotsky() {
    echo "Building Grotsky $GROTSKY_VERSION from source (UTF-8 lexer fix)..."
    BUILD_DIR=$(mktemp -d)
  trap 'rm -rf "$BUILD_DIR"' EXIT

    git clone --depth 1 --branch v0.0.19 https://github.com/mliezun/grotsky.git "$BUILD_DIR"
    patch -p1 -d "$BUILD_DIR" < "$REPO_ROOT/scripts/grotsky-utf8.patch"
    (cd "$BUILD_DIR" && cargo build --release)

    mkdir -p "$GROTSKY_FOLDER"
    cp "$BUILD_DIR/target/release/grotsky-rs" "$GROTSKY_BINARY"
    chmod +x "$GROTSKY_BINARY"
    echo "Built patched Grotsky at $GROTSKY_BINARY"
}

if [ ! -f "$GROTSKY_BINARY" ]; then
    mkdir -p "$GROTSKY_FOLDER"
    RELEASE_URL="https://github.com/mliezun/grotsky/releases/download/$GROTSKY_RELEASE/$GROTSKY_TARGZ"

    if wget "$RELEASE_URL" -P "$GROTSKY_FOLDER" -q; then
        echo "Downloading Grotsky $GROTSKY_VERSION..."
        tar -xvf "$GROTSKY_FOLDER/$GROTSKY_TARGZ" -C "$GROTSKY_FOLDER" > /dev/null 2>&1
        rm -f "$GROTSKY_FOLDER/$GROTSKY_TARGZ"
        chmod +x "$GROTSKY_BINARY"
        echo "Grotsky binary ready at $GROTSKY_BINARY"
    else
        rm -f "$GROTSKY_FOLDER/$GROTSKY_TARGZ"
        build_patched_grotsky
    fi
fi
