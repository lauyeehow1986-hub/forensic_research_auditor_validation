#!/usr/bin/env python3
"""
Tests Europe PMC cursor pagination with 1,000 results per request.
"""

import json
import time
import urllib.parse
import urllib.request


def fetch_clean_controls_batch(target: int = 5000):
    query = 'PUB_TYPE:"Journal Article" AND OPEN_ACCESS:y NOT PUB_TYPE:"Retracted Publication"'
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    cursor = "*"
    collected = []
    t0 = time.time()

    print(f"Fetching {target} real clean controls from Europe PMC (1,000 per page)...")
    page = 1
    while len(collected) < target:
        remaining = target - len(collected)
        page_size = min(1000, remaining)
        url = f"{base_url}?query={urllib.parse.quote(query)}&format=json&pageSize={page_size}&resultType=lite&cursorMark={cursor}"
        req = urllib.request.Request(url, headers={"User-Agent": "Antigravity10kValidator/1.0"})
        
        t_page = time.time()
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        
        results = data.get("resultList", {}).get("result", [])
        if not results:
            break
        
        for r in results:
            collected.append({
                "id": r.get("id"),
                "pmcid": r.get("pmcid"),
                "doi": r.get("doi"),
                "title": r.get("title", ""),
                "journal": r.get("journalTitle", ""),
                "year": r.get("pubYear", "")
            })
            if len(collected) >= target:
                break
        
        cursor = data.get("nextCursorMark")
        print(f"  • Page {page}: fetched {len(results)} controls ({time.time() - t_page:.2f}s). Total so far: {len(collected)}")
        page += 1
        if not cursor:
            break
        time.sleep(0.5)

    print(f"Successfully collected {len(collected)} clean controls in {time.time() - t0:.2f}s!")
    return collected


if __name__ == "__main__":
    controls = fetch_clean_controls_batch(5000)
    print("Sample control study:")
    print(json.dumps(controls[0], indent=2))
