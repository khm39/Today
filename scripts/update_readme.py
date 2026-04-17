#!/usr/bin/env python3
"""Regenerate README.md with an index of daily summary files.

Daily files live at ./YYYY/MM/DD.md. This script scans those paths,
groups them by year and month, and renders an index between the markers
defined below while preserving any surrounding hand-written content.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
START_MARKER = "<!-- DAILY_INDEX:START -->"
END_MARKER = "<!-- DAILY_INDEX:END -->"

DATE_PATTERN = re.compile(r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})\.md$")

HEADER = """# Today

毎日の天気・株式市場・記念日・豆知識をまとめた日次サマリーのアーカイブです。

## 📚 日次サマリー一覧
"""


def collect_entries() -> dict[str, dict[str, list[str]]]:
    entries: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for path in ROOT.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9].md"):
        rel = path.relative_to(ROOT).as_posix()
        match = DATE_PATTERN.match(rel)
        if not match:
            continue
        entries[match["year"]][match["month"]].append(match["day"])
    return entries


def render_index(entries: dict[str, dict[str, list[str]]]) -> str:
    if not entries:
        return "\n_まだ日次サマリーはありません。_\n"

    lines: list[str] = []
    for year in sorted(entries.keys(), reverse=True):
        lines.append(f"\n### {year}年")
        months = entries[year]
        for month in sorted(months.keys(), reverse=True):
            days = sorted(months[month], reverse=True)
            day_links = ", ".join(
                f"[{int(day)}日]({year}/{month}/{day}.md)" for day in days
            )
            lines.append(f"- **{int(month)}月**: {day_links}")
    lines.append("")
    return "\n".join(lines)


def build_readme(index_block: str) -> str:
    wrapped = f"{START_MARKER}\n{index_block}\n{END_MARKER}"

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
    entries = collect_entries()
    index_block = render_index(entries)
    README.write_text(build_readme(index_block), encoding="utf-8")


if __name__ == "__main__":
    main()
