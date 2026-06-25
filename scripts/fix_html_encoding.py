#!/usr/bin/env python3
"""Fix Grotsky double-UTF-8 encoding in generated HTML files."""

from pathlib import Path


def fix_mojibake(text: str) -> str:
    # Grotsky double-encodes some UTF-8 characters in HTML output. A full-file
    # latin-1 roundtrip fails when pages contain emoji or other non-Latin-1 text,
    # so apply targeted replacements instead.
    replacements = (
        ("Â·", "·"),
        ("â€™", "'"),
        ("â€œ", '"'),
        ("â€\u009d", '"'),
        ("â€”", "—"),
        ("â€“", "–"),
        ("â†’", "→"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def main() -> None:
    docs = Path("docs")
    for path in docs.rglob("*.html"):
        original = path.read_text(encoding="utf-8")
        fixed = fix_mojibake(original)
        if fixed != original:
            path.write_text(fixed, encoding="utf-8")


if __name__ == "__main__":
    main()
