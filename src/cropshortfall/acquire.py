"""Lawful acquisition of public crop-statistics sources with checksum manifest.

Raw files are written outside Git (default ``data/raw/``, which is gitignored).
Each host gets at most ``MAX_ATTEMPTS`` ordinary attempts with short timeouts;
no access controls are bypassed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

MAX_ATTEMPTS = 3
TIMEOUT_S = 60

DRYAD = "https://datadryad.org"
HARVESTSTAT_DOI = "doi:10.5061/dryad.vq83bk42w"


@dataclass
class SourceFile:
    source_id: str
    name: str
    url: str
    expected_sha256: str | None
    license: str
    landing: str


# Dryad version 12 (published 2026-07-17); digests are the ones Dryad reports.
HARVESTSTAT_FILES = [
    SourceFile("harveststat_africa_v1.2", "hvstat_africa_data_v1.2.csv",
               f"{DRYAD}/api/v2/files/4864223/download",
               "f659e121e315b9d8656699e4b16421ed3b313e4c8d09d15199452000836dbef9",
               "CC0-1.0", "https://doi.org/10.5061/dryad.vq83bk42w"),
    SourceFile("harveststat_africa_v1.2", "README.md",
               f"{DRYAD}/api/v2/files/4864379/download",
               "d6dc9a64cd0f20c955f7f4f8e0305a27661fa98870fa4010700f58a543fe2d20",
               "CC0-1.0", "https://doi.org/10.5061/dryad.vq83bk42w"),
    SourceFile("harveststat_africa_v1.2", "CHANGELOG.md",
               f"{DRYAD}/api/v2/files/4864224/download",
               "ad21f228188aff94306e9f9c9bff53fac5562acc9d87b2be495083fe6eafad74",
               "CC0-1.0", "https://doi.org/10.5061/dryad.vq83bk42w"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


_HOST_ATTEMPTS: Counter = Counter()


def _take_attempt(url: str) -> bool:
    """Enforce at most MAX_ATTEMPTS ordinary requests per host per run."""
    host = urllib.parse.urlparse(url).netloc
    if _HOST_ATTEMPTS[host] >= MAX_ATTEMPTS:
        return False
    _HOST_ATTEMPTS[host] += 1
    return True


def fetch(src: SourceFile, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / src.name
    record = asdict(src) | {"path": str(dest), "attempts": 0, "status": None,
                            "error": None}
    if dest.exists() and src.expected_sha256 and sha256_file(dest) == src.expected_sha256:
        record["status"] = "cached"
    else:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            if not _take_attempt(src.url):
                record["status"] = record["status"] or "skipped_host_budget"
                break
            record["attempts"] = attempt
            try:
                req = urllib.request.Request(src.url, headers={"User-Agent": "r06-audit/0.1"})
                with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp, dest.open("wb") as fh:
                    record["http_status"] = resp.status
                    while chunk := resp.read(1 << 20):
                        fh.write(chunk)
                record["status"] = "downloaded"
                break
            except Exception as exc:  # recorded, never silently ignored
                record["error"] = f"{type(exc).__name__}: {exc}"
                record["status"] = "failed"
                if getattr(exc, "code", None) in (401, 403):
                    break  # access control: do not retry or work around
                time.sleep(2 ** attempt)
    if dest.exists():
        record["bytes"] = dest.stat().st_size
        record["sha256"] = sha256_file(dest)
        record["sha256_matches_source"] = (record["sha256"] == src.expected_sha256
                                           if src.expected_sha256 else None)
    record["accessed_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return record


# Public GitHub mirror maintained by the HarvestStat authors (MIT per repo
# LICENSE); pinned to the commit audited on 2026-10-17.
HARVESTSTAT_GIT = "https://github.com/HarvestStat/HarvestStat-Africa.git"
HARVESTSTAT_GIT_COMMIT = "c80b451df014e6a15aed75e70cd9c2ddd3631f82"


def fetch_git_public(out_dir: Path, clone_dir: Path) -> list[dict]:
    """Sparse, blob-filtered clone of ``public/`` and checksum of each file."""
    if not clone_dir.exists():
        if not _take_attempt(HARVESTSTAT_GIT):
            return [{"source_id": "harveststat_git", "status": "skipped_host_budget"}]
        subprocess.run(["git", "clone", "--filter=blob:none", "--sparse", "--depth", "50",
                        HARVESTSTAT_GIT, str(clone_dir)], check=True, timeout=300)
        subprocess.run(["git", "-C", str(clone_dir), "sparse-checkout", "set", "public"],
                       check=True, timeout=300)
    head = subprocess.run(["git", "-C", str(clone_dir), "rev-parse", "HEAD"], check=True,
                          capture_output=True, text=True).stdout.strip()
    commit_time = subprocess.run(["git", "-C", str(clone_dir), "log", "-1", "--format=%cI"],
                                 check=True, capture_output=True, text=True).stdout.strip()
    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for f in sorted((clone_dir / "public").glob("*")):
        if f.suffix not in {".csv", ".md"}:
            continue
        dest = out_dir / f.name
        dest.write_bytes(f.read_bytes())
        records.append({"source_id": "harveststat_africa_git", "name": f.name,
                        "url": f"{HARVESTSTAT_GIT}#public/{f.name}", "git_commit": head,
                        "git_commit_time": commit_time,
                        "pinned_commit_matches": head == HARVESTSTAT_GIT_COMMIT,
                        "license": "MIT (repository LICENSE); Dryad record lists CC0-1.0",
                        "status": "copied", "bytes": dest.stat().st_size,
                        "sha256": sha256_file(dest),
                        "accessed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    return records


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="data/raw/harveststat", type=Path)
    ap.add_argument("--manifest", default="results/tables/acquisition_manifest.json", type=Path)
    ap.add_argument("--clone-dir", default="data/raw/_harveststat_git", type=Path)
    args = ap.parse_args()
    records = [fetch(s, args.out / "dryad") for s in HARVESTSTAT_FILES]
    for r in records:
        r["path"] = Path(r["path"]).name  # do not leak local paths into Git
    records += fetch_git_public(args.out, args.clone_dir)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(records, indent=2) + "\n")
    for r in records:
        print(r.get("name"), r["status"], r.get("bytes"), r.get("sha256", "")[:12], r.get("error"))


if __name__ == "__main__":
    main()
