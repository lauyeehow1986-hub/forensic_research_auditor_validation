#!/usr/bin/env python3
"""
Downloads and parses the official Crossref Retraction Watch CSV dataset.
"""

import csv
import os
import sys
import time
import urllib.request

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw_benchmarks"))
CSV_PATH = os.path.join(DATA_DIR, "retraction_watch_full.csv")


def download_retraction_watch_csv():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 10 * 1024 * 1024:
        print(f"Retraction Watch CSV already exists at {CSV_PATH} ({os.path.getsize(CSV_PATH) / (1024*1024):.2f} MB).")
        return CSV_PATH

    url = "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv"
    print(f"Downloading official Crossref Retraction Watch CSV from:\n  {url}")
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "Antigravity10kAuditor/2.0"})
    
    with urllib.request.urlopen(req, timeout=60) as resp, open(CSV_PATH, "wb") as f:
        total_bytes = 0
        while True:
            chunk = resp.read(1024 * 512)
            if not chunk:
                break
            f.write(chunk)
            total_bytes += len(chunk)
            print(f"\rDownloaded {total_bytes / (1024*1024):.2f} MB...", end="", flush=True)

    elapsed = time.time() - t0
    print(f"\nDownload complete in {elapsed:.2f}s ({os.path.getsize(CSV_PATH) / (1024*1024):.2f} MB).")
    return CSV_PATH


if __name__ == "__main__":
    csv_file = download_retraction_watch_csv()
    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        count = sum(1 for _ in reader)
    print(f"Total Retraction Watch records in database: {count:,}")
