"""自作スキルを掲載用にサニタイズする。

~/.claude/skills から複製済みの skills/ を対象に、
個人・取引先の識別子をプレースホルダへ置換する。
置換結果は report.md に出力し、置換漏れは exit code 1 で知らせる。

置換ルールは rules.py に置く（公開しない）。ひな形は rules.example.py。
"""

import logging
import re
import sys
from collections import Counter
from pathlib import Path

from rules import FORBIDDEN, RULES

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "skills"

def main() -> int:
    if not TARGET.is_dir():
        logger.error("対象が見つからない: %s", TARGET)
        return 1

    counts: Counter[str] = Counter()
    touched: list[str] = []

    for path in sorted(TARGET.rglob("*")):
        if not path.is_file() or path.name == ".DS_Store":
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("バイナリのためスキップ: %s", path)
            continue

        text = original
        for label, pattern, replacement in RULES:
            text, n = re.subn(pattern, replacement, text)
            if n:
                counts[label] += n

        if text != original:
            path.write_text(text, encoding="utf-8")
            touched.append(str(path.relative_to(TARGET)))

    # 検証
    leaks: list[str] = []
    for path in sorted(TARGET.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if FORBIDDEN.search(line):
                leaks.append(f"{path.relative_to(TARGET)}:{i}: {line.strip()[:120]}")

    report = ROOT / "report.md"
    lines = ["# サニタイズ結果", "", "## 置換件数", ""]
    lines += [f"- {label}: {n}件" for label, n in counts.most_common()] or ["- なし"]
    lines += ["", f"## 変更したファイル（{len(touched)}件）", ""]
    lines += [f"- {t}" for t in touched] or ["- なし"]
    lines += ["", f"## 置換漏れ（{len(leaks)}件）", ""]
    lines += [f"- `{l}`" for l in leaks] or ["- なし"]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    logger.info("置換 %d件 / 変更ファイル %d件 / 漏れ %d件", sum(counts.values()), len(touched), len(leaks))
    logger.info("レポート: %s", report)
    return 1 if leaks else 0


if __name__ == "__main__":
    sys.exit(main())
