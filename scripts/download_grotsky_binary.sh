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

GROTSKY_VERSION=v0.0.16
GROTSKY_RELEASE=${GROTSKY_VERSION}

GROTSKY_FOLDER=.grotsky

GROTSKY_TARGZ=grotsky-$GROTSKY_VERSION-$OS-$ARCH.tar.gz
GROTSKY_BINARY=$GROTSKY_FOLDER/grotsky

if [ ! -f "$GROTSKY_BINARY" ]; then
    mkdir -p $GROTSKY_FOLDER
    echo "Downloading Grotsky Binary..."
    echo "https://github.com/mliezun/grotsky/releases/download/$GROTSKY_RELEASE/$GROTSKY_TARGZ"
    wget "https://github.com/mliezun/grotsky/releases/download/$GROTSKY_RELEASE/$GROTSKY_TARGZ" -P $GROTSKY_FOLDER > /dev/null 2>&1
    tar -xvf $GROTSKY_FOLDER/$GROTSKY_TARGZ -C $GROTSKY_FOLDER > /dev/null 2>&1
    chmod +x $GROTSKY_BINARY
    echo "Grotsky Binary downloaded and extracted to $GROTSKY_BINARY"
    echo "Cleaning up..."
    # Remove the tar.gz file
    rm -rf $GROTSKY_FOLDER/$GROTSKY_TARGZ
    echo "Done!"
fi
