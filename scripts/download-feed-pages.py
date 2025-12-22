#!/usr/bin/env python3
"""
Debug tool. Download the feed and write items' <description> HTML to files.

- Feed URL: http://localhost:1313/blog/index.xml
- Output dir: ./feed_items
- Filename: last non-empty path segment of each item's <link>, plus ".html"
- Writes the description HTML *exactly as-is* (no wrapping/template, no escaping)
"""

import pathlib
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

FEED_URL = "http://localhost:1313/blog/index.xml"
OUT_DIR = pathlib.Path(__file__).parent / "feed_items"


def filename_from_url(url: str) -> str:
    """Last non-empty path segment from URL, sanitized, with .html."""
    base = re.sub(
        r"[^A-Za-z0-9._-]+", "-",
        [s for s in urllib.parse.urlparse(url).path.split("/") if s][-1]
    ).strip("-._")
    return f"{base}.html"


def endswith(tag: str, name: str) -> bool:
    """True if XML tag is either 'name' or '*}name' (namespace-agnostic)."""
    return tag == name or tag.endswith("}" + name)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Fetch feed
    with urllib.request.urlopen(FEED_URL) as resp:
        data = resp.read()

    # Parse XML
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        sys.stderr.write(f"XML parse error: {e}\n")
        sys.exit(1)

    # Collect <item> elements (RSS), namespace-agnostic
    items = [el for el in root.iter() if endswith(el.tag, "item")]
    if not items:
        sys.stderr.write("No <item> elements found. Is this an RSS feed?\n")
        sys.exit(1)

    for item in items:
        link = ""
        desc_html = ""

        for child in list(item):
            if endswith(child.tag, "link") and (child.text or "").strip():
                link = child.text.strip()
            elif endswith(child.tag, "description"):
                # Take exactly the inner text (likely CDATA with HTML).
                desc_html = child.text or ""

        fname = filename_from_url(link)
        fpath = OUT_DIR / fname

        with open(fpath, "w", encoding="utf-8", newline="") as f:
            f.write(desc_html)

        print(f"Wrote {fpath}  ({len(desc_html)} bytes)")

    print(f"Wrote {len(items)} items into {OUT_DIR}/")


if __name__ == "__main__":
    main()
