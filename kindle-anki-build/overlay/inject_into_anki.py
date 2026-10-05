#!/usr/bin/env python3
"""Inject the independent semantic port module into a pinned Anki checkout.

The checkout commit is verified before modification. This script is deliberately
small and deterministic so the shipped backend can be reproduced from upstream.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--anki", type=Path, required=True)
    args = parser.parse_args()

    lock = json.loads((args.project / "upstream.lock.json").read_text())
    expected = lock["commit"]
    actual = subprocess.check_output(
        ["git", "-C", str(args.anki), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != expected:
        raise SystemExit(f"Anki checkout mismatch: expected {expected}, got {actual}")

    # The official Anki build reads Fluent input from exact pinned submodules.
    subprocess.run(
        [
            "git",
            "-C",
            str(args.anki),
            "submodule",
            "update",
            "--init",
            "--recursive",
            "--depth",
            "1",
        ],
        check=True,
    )

    target = args.anki / "rslib" / "src" / "kap_port.rs"
    shutil.copyfile(args.project / "core" / "src" / "port.rs", target)

    lib = args.anki / "rslib" / "src" / "lib.rs"
    text = lib.read_text()
    declaration = "pub mod kap_port;"
    if declaration not in text:
        anchor = "pub mod version;"
        if anchor not in text:
            raise SystemExit("Unable to find stable rslib module anchor")
        text = text.replace(anchor, anchor + "\n" + declaration, 1)
        lib.write_text(text)

    cargo = args.anki / "rslib" / "Cargo.toml"
    text = cargo.read_text()
    if "crate-type" not in text:
        text += '\n[lib]\ncrate-type = ["rlib", "cdylib"]\n'
        cargo.write_text(text)


if __name__ == "__main__":
    main()
