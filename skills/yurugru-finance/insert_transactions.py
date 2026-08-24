#!/usr/bin/env python3
"""ゆるグル収支DBへ取引行を一括投入する。

使い方:
    <venv>/python insert_transactions.py transactions.json

transactions.json の形式（配列）:
[
  {"name":"サンプル太郎","date":"2026-06-14","kind":"収入",
   "category":"投げ銭","amount":5000,"method":"Stripe","memo":"..."},
  ...
]

- amount は「円」の整数。USD等はスキル側で概算換算してから渡す。
- kind は "収入" or "支出"。収支額(式)が自動で符号を付ける。
"""
import os
import sys
import json
from dotenv import load_dotenv
from notion_client import Client

ENV_PATH = "/Users/you/projects/standby/case-management-package/.env"
DB_ID = "00000000000000000000000000000000"


def build_props(t: dict) -> dict:
    p = {
        "名前":   {"title": [{"text": {"content": t["name"]}}]},
        "日付":   {"date": {"start": t["date"]}},
        "種別":   {"select": {"name": t["kind"]}},
        "カテゴリ": {"select": {"name": t["category"]}},
        "金額":   {"number": int(t["amount"])},
    }
    if t.get("method"):
        p["支払方法"] = {"select": {"name": t["method"]}}
    if t.get("memo"):
        p["メモ"] = {"rich_text": [{"text": {"content": t["memo"]}}]}
    return p


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: insert_transactions.py transactions.json", file=sys.stderr)
        sys.exit(2)
    load_dotenv(ENV_PATH)
    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("NOTION_TOKEN が見つかりません（case-management-package/.env）", file=sys.stderr)
        sys.exit(2)
    client = Client(auth=token)

    with open(sys.argv[1], encoding="utf-8") as f:
        rows = json.load(f)

    income = expense = 0
    for t in rows:
        client.pages.create(
            parent={"type": "database_id", "database_id": DB_ID},
            properties=build_props(t),
        )
        amt = int(t["amount"])
        if t["kind"] == "収入":
            income += amt
        else:
            expense += amt
        print(f"[{t['kind']}] {t['date']} {t['name']} ¥{amt:,}")

    print(f"\nDONE inserted={len(rows)}  "
          f"収入計=¥{income:,}  支出計=¥{expense:,}  収支差引=¥{income - expense:,}")


if __name__ == "__main__":
    main()
