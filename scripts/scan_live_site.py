#!/usr/bin/env python3
"""Scan live mliezun.com pages for rendering/HTML issues."""

from __future__ import annotations

import glob
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict

BASE = "https://mliezun.com"
UA = {"User-Agent": "Mozilla/5.0 (compatible; mliezun-site-scan/1.0)"}


def fetch(path: str) -> tuple[int, str]:
    url = BASE + (path if path != "/" else "/")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def local_paths() -> list[str]:
    paths = []
    for file in glob.glob("docs/**/*.html", recursive=True):
        rel = file.removeprefix("docs")
        if rel == "/index.html":
            paths.append("/")
        else:
            paths.append(rel)
    return sorted(set(paths))


def check_html(path: str, html: str) -> list[str]:
    problems: list[str] = []

    if path.endswith(".html") or path == "/":
        if "Â·" in html:
            problems.append("mojibake: Â· in page")
        if re.search(r"class=\"archive-entry\"[\s\S]{0,800}ai-tag-read-more", html):
            problems.append("invalid nested link in archive entry")
        if "<main" not in html and "google" not in path:
            problems.append("missing <main> landmark")
        if "/assets/css/style.css" not in html and "google" not in path:
            problems.append("missing site stylesheet")
        if "masthead-title" not in html and "google" not in path:
            problems.append("missing masthead title")

    if path == "/":
        entries = len(re.findall(r'class="archive-entry"', html))
        if entries != 41:
            problems.append(f"homepage has {entries} archive entries (expected 41)")
        years = re.findall(r'id="year-(\d{4})"', html)
        if years and years[0] != max(years):
            problems.append(f"archive years start with {years[0]} (expected {max(years)} first)")

    if re.match(r"/20\d\d/", path):
        if "<article" not in html:
            problems.append("article page missing <article>")
        if "journal-meta-wrap" not in html and "article-byline" not in html:
            problems.append("article missing byline/metadata")

    assets = set(re.findall(r'(?:src|href)="(/assets/[^"]+)"', html))
    for asset in assets:
        try:
            fetch(asset)
        except urllib.error.HTTPError as exc:
            problems.append(f"broken asset {asset} ({exc.code})")
        except Exception as exc:  # noqa: BLE001
            problems.append(f"broken asset {asset} ({exc})")

    return problems


def main() -> int:
    issues: dict[str, list[str]] = defaultdict(list)
    paths = [p for p in local_paths() if "google" not in p]

    for path in paths:
        try:
            status, html = fetch(path)
        except Exception as exc:  # noqa: BLE001
            issues[path].append(f"fetch failed: {exc}")
            continue
        if status != 200:
            issues[path].append(f"HTTP {status}")
        issues[path].extend(check_html(path, html))

    problems = {path: probs for path, probs in issues.items() if probs}
    if not problems:
        print(f"OK: scanned {len(paths)} pages, no issues found")
        return 0

    print(f"Issues on live site ({len(problems)} pages):\n")
    for path, probs in sorted(problems.items()):
        print(path)
        for prob in probs:
            print(f"  - {prob}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
