#!/usr/bin/env python3
"""Fix Grotsky double-UTF-8 encoding in generated HTML files."""

from pathlib import Path


def fix_mojibake(text: str) -> str:
    if "Â" not in text and "â" not in text:
        return text
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
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
