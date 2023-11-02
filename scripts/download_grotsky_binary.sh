#!/bin/bash

set -euo pipefail

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "OS not supported."
    exit 1
fi

GROTSKY_VERSION=v0.0.6
GROTSKY_RELEASE=${GROTSKY_VERSION}

GROTSKY_FOLDER=.grotsky

GROTSKY_TARGZ=grotsky-$GROTSKY_VERSION-$OS-x86_64.tar.gz

if [ ! -f "$GROTSKY_FOLDER/grotsky" ]; then
    mkdir -p $GROTSKY_FOLDER
    echo "Downloading Grotsky Binary..."
    echo "https://github.com/mliezun/grotsky/releases/download/$GROTSKY_RELEASE/$GROTSKY_TARGZ"
    wget "https://github.com/mliezun/grotsky/releases/download/$GROTSKY_RELEASE/$GROTSKY_TARGZ" -P $GROTSKY_FOLDER > /dev/null 2>&1
    tar -xvf $GROTSKY_FOLDER/$GROTSKY_TARGZ -C $GROTSKY_FOLDER > /dev/null 2>&1
    rm -rf $GROTSKY_FOLDER/$GROTSKY_TARGZ
    echo "Done!"
fi
