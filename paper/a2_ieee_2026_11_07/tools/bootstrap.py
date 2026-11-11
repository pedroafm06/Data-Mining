#!/usr/bin/env python3
"""Fetch the pinned, verified Tectonic release into this paper's work/bin.

No installation, shell-piped scripts, PATH changes, or administrator privileges.
The official vendored IEEEtran distribution is already included in the source.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import platform
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "A2-IEEE-reproducible-build"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def main() -> None:
    lock = json.loads((ROOT / "provenance.lock.json").read_text())
    spec = lock["tectonic"]
    if (platform.system(), platform.machine()) != ("Darwin", "arm64"):
        raise SystemExit("This pinned binary is macOS arm64. Select an official release asset and update the provenance lock for another platform.")
    binary = ROOT / "work/bin/tectonic"
    if binary.exists() and sha256(binary.read_bytes()) == spec["executable_sha256"]:
        print("Verified local Tectonic binary:", binary)
        return
    release = json.loads(fetch(spec["release_api"]))
    asset = next(a for a in release["assets"] if a["id"] == spec["asset_id"])
    expected_digest = "sha256:" + spec["sha256"]
    if asset.get("digest") != expected_digest or asset["browser_download_url"] != spec["url"]:
        raise SystemExit("Official GitHub metadata differs from the pinned release; stopped.")
    archive = fetch(spec["url"])
    if sha256(archive) != spec["sha256"]:
        raise SystemExit("Tectonic archive SHA-256 mismatch; stopped.")
    downloads = ROOT / "work/downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    (downloads / Path(spec["url"]).name).write_bytes(archive)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
        member = next(m for m in bundle.getmembers() if Path(m.name).name == "tectonic" and m.isfile())
        executable = bundle.extractfile(member).read()
    if sha256(executable) != spec["executable_sha256"]:
        raise SystemExit("Extracted executable SHA-256 mismatch; stopped.")
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.write_bytes(executable)
    binary.chmod(0o755)
    print("Installed and verified only inside:", binary.parent)


if __name__ == "__main__":
    main()
