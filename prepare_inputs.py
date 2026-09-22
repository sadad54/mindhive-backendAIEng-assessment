"""Acquire pinned upstream fixtures locally, or copy an existing offline checkout.

This preparation step is separate from offline evaluation. It does not publish files.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


def prepare(root, source=None):
    manifest = json.loads((root / "docs/INPUT_MANIFEST.json").read_text())
    revision = manifest["source_revision"]
    repository = manifest["source_repository"]
    for name, expected in manifest["files"].items():
        target = root / name
        if target.exists():
            raw = target.read_bytes()
        elif source:
            raw = (source / name).read_bytes()
        else:
            url = f"https://raw.githubusercontent.com/{repository}/{revision}/{name}"
            with urlopen(url, timeout=30) as response:
                raw = response.read()
        if hashlib.sha256(raw).hexdigest() != expected["sha256"]:
            raise ValueError(f"Checksum mismatch; not overwriting {name}")
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + ".download")
            temporary.write_bytes(raw)
            temporary.replace(target)
        print(f"Verified {name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Existing original assessment checkout (offline)")
    args = parser.parse_args()
    prepare(Path(__file__).parent, args.source)
