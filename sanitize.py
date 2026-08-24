"""自作スキルを Kindle 掲載用にサニタイズする。

~/.claude/skills から複製済みの skills/ を対象に、
個人・取引先の識別子をプレースホルダへ置換する。
置換結果は report.md に出力し、置換漏れは exit code 1 で知らせる。
"""

import logging
import re
import sys
from collections import Counter
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "skills"

# 上から順に適用する。順序に意味がある（メールアドレスを先に潰す）
RULES: list[tuple[str, str, str]] = [
    # (説明, 正規表現, 置換後)
    ("カレンダーID(本業)", r"78c706[0-9a-f]+@group\.calendar\.google\.com", "work-calendar-id@group.calendar.google.com"),
    ("メールアドレス", r"[A-Za-z0-9._%+-]+@(?!example\.com|group\.calendar\.google\.com)[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "you@example.com"),
    ("Notion ID(UUID形式)", r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", "00000000-0000-0000-0000-000000000000"),
    ("Notion ID(32桁)", r"\b[0-9a-f]{32}\b", "0" * 32),
    ("本業名(JHC)", r"JHC|Japan Healthcare|jhc", "本業"),
    ("取引先(KANCHI)", r"KANCHI", "業務委託先A"),
    ("取引先(WEEL)", r"WEEL", "オウンドメディアA"),
    ("顧問先(流動食協会)", r"流動食協会", "顧問先B"),
    ("協業先(新田)", r"新田さん|新田", "協業先C"),
    ("ホームディレクトリ", r"/Users/shohei", "/Users/you"),
    ("氏名(ローマ字)", r"Shohei Kondo|Shohei|shohei", "You"),
    ("氏名(漢字)", r"近藤翔平|翔平", "著者"),
    ("サンプルデータの実名", r"寛子 椛島|椛島 寛子|椛島|寛子", "サンプル太郎"),
    ("関係者の実名", r"小林さん|小林|佐野さん|佐野|翔平", "担当者"),
    ("GA4プロパティID", r"\b521516653\b", "000000000"),
    # 置換の結果おかしくなった表記を整える（順序上、必ず最後）
    ("重複置換の整形", r"本業（本業）|本業\(本業\)", "本業"),
    ("重複置換の整形2", r"本業著者スケジュール", "本業スケジュール"),
]

# 置換後にこれが残っていたら失敗とみなす
FORBIDDEN = re.compile(
    r"JHC|jhc|KANCHI|WEEL|流動食|新田|shohei|Shohei|翔平|小林|佐野|椛島|"
    r"\b(?!0{32})[0-9a-f]{32}\b|@group\.calendar\.google\.com(?<!work-calendar-id@group\.calendar\.google\.com)"
)


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
