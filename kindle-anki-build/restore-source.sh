#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
base64 --decode source.b64 > source.zip
sha256sum -c source.sha256
rm -rf kindle-anki-port
unzip -q source.zip
[ -f kindle-anki-port/core/src/port.rs ]
printf '%s\n' "Restored Kindle Anki source"
