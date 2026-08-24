---
name: done
description: 作業完了を今日のObsidianデイリーノートに記録する。「/done {完了内容}」の形式で呼び出す。
---

# /done — 完了ログ記録スキル

作業が終わったタイミングで `/done {完了内容}` と打つと、今日のデイリーノートに完了記録を追記する。

## 使い方

```
/done LP修正完了、先方にメール送付済み
/done migrate.py 本番実行、S3→GDrive移行完了
/done [本業] 担当者返信メール送信
/done [個人] ゆるふわ学会メシ カテゴリ機能リリース
/done [中断] RAGチャットボット、Supabase接続エラーで一旦保留
```

## 実行手順

### 1. 引数（完了内容）を解析する

- `/done` に続くテキスト全体が完了内容
- `[本業]` / `[個人]` / `[中断]` / `[保留]` が含まれていればそのまま使う
- タグがない場合はキーワードから自動判定：
  - 本業 / AWS / S3 / 発注 / 医療 / インソール / 足 / 担当者 / 協業先C / 担当者 → `[本業]`
  - それ以外 → `[個人]`

### 2. 今日のデイリーノートに追記する

以下のPythonスクリプトを実行して追記する：

```bash
python3 << 'EOF'
import os
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
time_str = datetime.now().strftime("%H:%M")
vault_path = "/Users/you/Documents/Obsidian Vault/Daily"
note_path = f"{vault_path}/{today}.md"

# 追記する行（ARGSは実際の完了内容とタグに置換）
entry = f"- {time_str} ✅ [TAG] CONTENT\n"

# ファイルが存在しない場合は作成
if not os.path.exists(note_path):
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(f"# {today}\n\n## 完了ログ\n")

# 既存ファイルに「## 完了ログ」セクションがなければ追加してから追記
with open(note_path, "r", encoding="utf-8") as f:
    content = f.read()

if "## 完了ログ" not in content:
    content += "\n## 完了ログ\n"
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(content)

with open(note_path, "a", encoding="utf-8") as f:
    f.write(entry)

print(f"✅ 記録完了: {note_path}")
EOF
```

### 3. 完了を報告する

記録した内容を一行で表示する：

```
✅ 記録しました → 14:32 [個人] ゆるふわ学会メシ カテゴリ機能リリース
```

## 記録フォーマット

```
## 完了ログ
- 09:45 ✅ [本業] 担当者返信メール送信
- 11:20 ✅ [個人] note記事下書き完了
- 14:32 ✅ [個人] ゆるふわ学会メシ ads.txt追加・デプロイ
- 16:00 ✅ [中断] RAGチャットボット、Supabase接続エラーで保留
```

## 注意事項

- 完了だけでなく「中断」「保留」もそのまま記録してよい（後から振り返りやすくなる）
- タグが自動判定で合っていない場合は `[本業]` や `[個人]` を冒頭に明示すればOK
- 今日のデイリーノートが存在しない場合は自動で作成する
