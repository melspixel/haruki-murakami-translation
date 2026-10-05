#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
cat src.part-* | base64 --decode > source.zip
sha256sum -c source.sha256
rm -rf kindle-anki-port
unzip -q source.zip
if [ -f "$HERE/overlay/inject_into_anki.py" ]; then
    cp "$HERE/overlay/inject_into_anki.py" "$HERE/kindle-anki-port/tools/inject_into_anki.py"
    chmod 755 "$HERE/kindle-anki-port/tools/inject_into_anki.py"
fi
[ -f kindle-anki-port/core/src/port.rs ]
printf '%s\n' "Restored Kindle Anki source"
