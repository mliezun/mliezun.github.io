#!/bin/bash

set -e

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "OS not supported."
    exit 1
fi

GROTSKY_VERSION=v0.0.2

GROTSKY_FOLDER=.grotsky

GROTSKY_TARGZ=grotsky-$GROTSKY_VERSION-$OS-x86_64.tar.gz

if [ ! -f "$GROTSKY_FOLDER/grotsky" ]; then
    echo "Downloading Grotsky Binary..."
    wget "https://github.com/mliezun/grotsky/releases/download/$GROTSKY_VERSION/$GROTSKY_TARGZ" -P $GROTSKY_FOLDER > /dev/null 2>&1
    tar -xvf $GROTSKY_FOLDER/$GROTSKY_TARGZ -C $GROTSKY_FOLDER > /dev/null 2>&1
    rm -rf $GROTSKY_FOLDER/$GROTSKY_TARGZ
    echo "Done!"
fi

