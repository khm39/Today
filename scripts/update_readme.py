#!/usr/bin/env python3
"""Regenerate README.md to embed the latest daily summary.

Daily files live at ./YYYY/MM/DD.md. This script finds the newest one
and embeds its content between the markers below, preserving any
surrounding hand-written text in README.md.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
START_MARKER = "<!-- TODAY:START -->"
END_MARKER = "<!-- TODAY:END -->"

DATE_PATTERN = re.compile(r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})\.md$")

HEADER = """# Today

日々の天気・株式市場・記念日・豆知識を自動でまとめるデイリーサマリーアーカイブ。

毎日のサマリーは `YYYY/MM/DD.md` に保存され、最新分が以下に表示されます。
"""


def latest_daily_file() -> Path | None:
    candidates: list[tuple[str, Path]] = []
    for path in ROOT.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9].md"):
        rel = path.relative_to(ROOT).as_posix()
        if DATE_PATTERN.match(rel):
            candidates.append((rel, path))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[-1][1]


def build_readme(body: str) -> str:
    wrapped = f"{START_MARKER}\n{body}\n{END_MARKER}"
    if README.exists():
        current = README.read_text(encoding="utf-8")
        if START_MARKER in current and END_MARKER in current:
            pattern = re.compile(
                re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
                re.DOTALL,
            )
            return pattern.sub(wrapped, current)
    return f"{HEADER}\n{wrapped}\n"


def main() -> None:
    latest = latest_daily_file()
    body = (
        latest.read_text(encoding="utf-8").strip()
        if latest is not None
        else "_まだサマリーはありません。_"
    )
    README.write_text(build_readme(body), encoding="utf-8")


if __name__ == "__main__":
    main()
