"""Download NSE end-of-day files and keep a checksum manifest.

Primary source is NSE's daily "PR" bundle. One zip per trading day holds the
price file (Pd), the corporate-actions file (Bc) and index values, and its
layout has been stable from 2019 to today, so one parser covers the whole
history.
"""
from __future__ import annotations

import csv
import hashlib
import io
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import requests

from . import config

BASE = "https://nsearchives.nseindia.com"
PR_URL = BASE + "/archives/equities/bhavcopy/pr/PR{d:%d%m%y}.zip"
SYMBOL_CHANGE_URL = BASE + "/content/equities/symbolchange.csv"
# Cross-check sources: the two "bhavcopy" formats.
LEGACY_URL = BASE + "/content/historical/EQUITIES/{d:%Y}/{mon}/cm{d:%d}{mon}{d:%Y}bhav.csv.zip"
UDIFF_URL = BASE + "/content/cm/BhavCopy_NSE_CM_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"
LEGACY_LAST_DAY = date(2024, 7, 5)   # last day NSE published the old format
UDIFF_FIRST_DAY = date(2024, 1, 2)   # first day the new format is in the archive

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) silkperfect-data-pull"}
MANIFEST_FIELDS = ["date", "file", "status", "bytes", "sha256"]
# A missing file this recent may simply not be published yet, so retry it.
RECHECK_DAYS = 7


def pr_path(d: date, pr_dir: Path = config.PR_DIR) -> Path:
    return pr_dir / f"{d:%Y}" / f"PR{d:%d%m%y}.zip"


def http_get(url: str, tries: int = 4) -> tuple[int, bytes]:
    """GET with retries. Returns (status, body); 404 is returned, not raised."""
    last: Exception | None = None
    for attempt in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=45)
            if r.status_code in (200, 404):
                return r.status_code, r.content
            last = RuntimeError(f"HTTP {r.status_code} for {url}")
        except requests.RequestException as exc:
            last = exc
        time.sleep(2 ** attempt)
    raise RuntimeError(f"giving up on {url}: {last}")


def is_zip(body: bytes) -> bool:
    try:
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            return bool(z.namelist())
    except zipfile.BadZipFile:
        return False


def read_manifest(path: Path = config.MANIFEST_PATH) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(newline="") as fh:
        return {row["date"]: row for row in csv.DictReader(fh)}


def write_manifest(rows: dict[str, dict], path: Path = config.MANIFEST_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
        w.writeheader()
        for key in sorted(rows):
            w.writerow(rows[key])


def _fetch_one(d: date, pr_dir: Path) -> dict:
    status, body = http_get(PR_URL.format(d=d))
    row = {"date": d.isoformat(), "file": "", "status": "missing", "bytes": 0, "sha256": ""}
    if status == 200 and is_zip(body):
        path = pr_path(d, pr_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        row.update(file=path.name, status="ok", bytes=len(body),
                   sha256=hashlib.sha256(body).hexdigest())
    return row


def fetch_range(start: date, end: date, pr_dir: Path = config.PR_DIR,
                manifest_path: Path = config.MANIFEST_PATH, workers: int = 4,
                today: date | None = None) -> dict[str, int]:
    """Download every PR bundle between start and end (inclusive).

    Every calendar day is tried, because NSE holds occasional weekend sessions
    (budget day, Diwali muhurat). Days with no file are remembered as "missing"
    so they are not requested again.
    """
    today = today or date.today()
    manifest = read_manifest(manifest_path)
    todo = []
    d = start
    while d <= end:
        row = manifest.get(d.isoformat())
        have = row and row["status"] == "ok" and pr_path(d, pr_dir).exists()
        settled_missing = (row and row["status"] == "missing"
                           and (today - d).days > RECHECK_DAYS)
        if not have and not settled_missing:
            todo.append(d)
        d += timedelta(days=1)

    counts = {"ok": 0, "missing": 0, "error": 0, "skipped": (end - start).days + 1 - len(todo)}

    def safe(day: date) -> dict | None:
        try:
            return _fetch_one(day, pr_dir)
        except RuntimeError as exc:
            print(f"  {day}: {exc}")
            return None

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for i, row in enumerate(pool.map(safe, todo), 1):
            if row is None:
                counts["error"] += 1
            else:
                manifest[row["date"]] = row
                counts[row["status"]] += 1
            if i % 200 == 0:
                print(f"  {i}/{len(todo)} days checked")
                write_manifest(manifest, manifest_path)
    write_manifest(manifest, manifest_path)
    return counts


def verify_manifest(pr_dir: Path = config.PR_DIR,
                    manifest_path: Path = config.MANIFEST_PATH) -> list[str]:
    """Return the dates whose file on disk no longer matches the manifest."""
    bad = []
    for key, row in read_manifest(manifest_path).items():
        if row["status"] != "ok":
            continue
        path = pr_path(date.fromisoformat(key), pr_dir)
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            bad.append(key)
    return bad


def fetch_symbol_changes(path: Path = config.SYMBOL_CHANGE_PATH) -> Path:
    status, body = http_get(SYMBOL_CHANGE_URL)
    if status != 200:
        raise RuntimeError("NSE symbol-change file not available")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return path


def fetch_crosscheck(d: date, out_dir: Path = config.CROSSCHECK_DIR) -> tuple[str, Path] | None:
    """Download the bhavcopy for one day. Returns (format, path) or None."""
    if d >= UDIFF_FIRST_DAY:
        fmt, url = "udiff", UDIFF_URL.format(d=d)
    else:
        fmt, url = "legacy", LEGACY_URL.format(d=d, mon=f"{d:%b}".upper())
    path = out_dir / f"{fmt}_{d:%Y%m%d}.zip"
    if not path.exists():
        status, body = http_get(url)
        if status != 200 or not is_zip(body):
            return None
        out_dir.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    return fmt, path
