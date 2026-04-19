#!/usr/bin/env python3
"""
verify_intelligence.py — lead-discovery intelligence markdown gate.

Scans a generated banker intelligence .md and enforces Rule 4 of
`cn-lead-safety`: every hard number (digit + banker unit) must have an
inline source citation within the same line or the immediately-following
line.

Usage:
    python3 verify_intelligence.py <intelligence.md>
    # exit 0 → every hard number has citation
    # exit 1 → one or more hard numbers lack citation (details on stderr)

"Hard number" uses the same pattern as the downstream financial-services
provenance_verify.py:  digits (optional thousands commas + decimal) + one
of the banker units 亿 / 万 / % / 元 / 亿元 / RMB / USD / CNY / HKD / M / B.

"Source citation" = on the same line or next line, any of:
    来源：/ 来源: / 源：/ Source: / source: / 据 / 据... / 根据 / 引自
    / [^] footnote marker / (URL...) inline link / PDF 引用 / 招股书 /
    年报 / 季报 / Tushare / 巨潮 / 天眼查 / 企查查

Design choices:
    - Same-line OR next-line window: banker bullets often read
      "营收 1088 亿元\n（来源：...）" so checking only same-line misses
      multi-line structure.
    - Substring check — deliberately coarse; we want to reject "raw
      number, zero source" prose, not police citation style.
"""
from __future__ import annotations
import re
import sys
import pathlib

UNITS = r"(?:亿元|亿|万|%|元|RMB|USD|CNY|HKD|M|B)"
NUM_CORE = r"\d+(?:,\d{3})*(?:\.\d+)?"
HARD_NUMBER = re.compile(rf"({NUM_CORE})\s*({UNITS})")

# Citation anchors — appearance of any of these tokens in the same or
# adjacent line counts as an inline source citation. Extend if the team
# adopts a new citation convention.
CITATION_ANCHORS = (
    "来源：", "来源:", "源：", "Source:", "source:",
    "据", "根据", "引自",
    "招股书", "年报", "季报", "半年报",
    "Tushare", "tushare", "巨潮", "cninfo", "CNINFO",
    "天眼查", "企查查", "国家企业信用",
    "上交所", "深交所", "港交所", "SSE", "SZSE", "HKEX",
    "东方财富", "Choice", "Wind", "同花顺",
    "财新", "21世纪", "第一财经", "中证", "上证", "财联社", "澎湃",
    # T3 / T4 financial portals frequently cited in banker intel memos —
    # surfaced 2026-04-19 BYD real-test: sina quote pages + stockstar
    # daily-flow news are common sources that were previously missing.
    "新浪财经", "新浪", "sina.com.cn",
    "证券之星", "stockstar",
    "金融界", "jrj.com",
    "华尔街见闻", "wallstreetcn",
    "中国经济网", "国证",
    # More T3 / T4 sources surfaced 2026-04-20 multi-company real-test
    # (CATL / Midea / Ping An): 中国基金报 (chnfund), 界面新闻 (jiemian),
    # 中鹏信评 (credit rating agency), plus a couple of peer rating shops.
    "中国基金报", "chnfund",
    "界面新闻", "jiemian",
    "中鹏信评", "中诚信", "联合资信", "大公国际",  # credit rating agencies
    "上海证券报", "证券日报", "证券时报",
    "雪球", "xueqiu",
    "派财经", "时代周报",
    "http://", "https://",
    "[^",  # markdown footnote marker
)


def has_citation(line: str, next_line: str | None) -> bool:
    """Does the line (or next line) contain any citation anchor?"""
    window = line + "\n" + (next_line or "")
    return any(a in window for a in CITATION_ANCHORS)


def scan(text: str) -> list[tuple[int, str, str, str]]:
    """Return list of (line_no, number, unit, snippet) lacking citation."""
    lines = text.splitlines()
    missing: list[tuple[int, str, str, str]] = []
    for i, line in enumerate(lines):
        next_line = lines[i + 1] if i + 1 < len(lines) else None
        for m in HARD_NUMBER.finditer(line):
            # whitelist year-like numbers: "2024" alone (no unit follows
            # actual-unit regex captures number+unit so "2024年" would
            # require 年 in the UNITS list — it isn't, which is right;
            # year mentions without units don't fire this check).
            if has_citation(line, next_line):
                continue
            missing.append(
                (i + 1, m.group(1), m.group(2), line.strip()[:120])
            )
    return missing


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_intelligence.py <intelligence.md>", file=sys.stderr)
        return 2
    p = pathlib.Path(argv[1])
    if not p.exists():
        print(f"file not found: {p}", file=sys.stderr)
        return 2
    text = p.read_text(encoding="utf-8", errors="replace")
    missing = scan(text)

    # Count total hard numbers (whether or not cited) for the summary line.
    total = 0
    for line in text.splitlines():
        total += len(HARD_NUMBER.findall(line))

    if not missing:
        print(
            f"OK: verify_intelligence clean on {p} "
            f"({total} hard numbers, all with inline citation)"
        )
        return 0

    covered = total - len(missing)
    print(
        f"FAIL: {len(missing)} of {total} hard numbers missing "
        f"inline source citation in {p}",
        file=sys.stderr,
    )
    for lineno, num, unit, snippet in missing[:60]:
        print(
            f"  L{lineno:>4}: '{num}{unit}' — no citation in this or next line",
            file=sys.stderr,
        )
        print(f"         context: {snippet!r}", file=sys.stderr)
    if len(missing) > 60:
        print(f"  ...and {len(missing) - 60} more truncated.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
