---
name: case-manager
description: Notion×Claude Codeの案件管理システムを操作する。「商談処理」「議事録」「案件作って」「確度更新」「案件の週次レポート」「パイプライン」「停滞案件」と言われたとき、または商談メモ/文字起こしを渡されたときに起動する。商談メモから議事録・タスク・確度更新案を作りNotionへ反映し、次回予定をGoogleカレンダーにZoom付きで登録する。
---

# 案件管理（case-manager）

Notion（SSOT）× 公式APIスクリプトで案件パイプラインを回すスキル。
プロジェクト: `/Users/you/projects/standby/case-management-package/`

## 起動時にまずやること

1. 作業ディレクトリとvenvを用意：
   ```bash
   cd /Users/you/projects/standby/case-management-package
   source .venv/bin/activate
   ```
   venvが無ければ `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`。

2. **重要・サンドボックス**：スクリプトは`.env`のNOTION_TOKENを読む。`.env`はサンドボックスで読み取り保護されているため、**Pythonスクリプトを動かすBashは必ず `dangerouslyDisableSandbox: true` で実行**する（そうしないと「NOTION_TOKENがありません」になる）。

3. クライアント指定は `--client demo`（デモ環境）。別クライアントは `config.<名>.json` を作って `--client <名>`。

## ユーザーの意図 → 操作の振り分け

| 言われたこと | 操作 |
|---|---|
| 商談メモ/文字起こしを渡された、「商談処理」「議事録登録」 | **A. 商談処理** |
| 「案件作って」「新規案件」 | **B. 案件作成** |
| 「週次レポート」「パイプライン」「停滞案件」「いまの案件状況」 | **C. レポート** |
| 「確度上げて/下げて」「ステータスを〜に」単発更新 | **D. 案件更新** |
| 「サンプル消して」「掃除」 | **E. クリーンアップ** |
| 「先方メール登録」「取引先登録」「連絡先入れて」 | **F. 連絡先登録** |
| 「お礼メール」「サンクスメール」 | **G. お礼メール下書き** |
| 「前日リマインド」「明日の商談のリマインド」「リマインドメール」 | **H. リマインドメール下書き** |

---

## A. 商談処理（メイン）

1. **商談メモから `meeting.json` を生成する**（あなた＝Claudeが整形）。スキーマ：
   ```json
   {
     "deal_name": "ABC商事 インソール導入",
     "meeting": {
       "title": "YYYY-MM-DD 取引先 商談",
       "date": "YYYY-MM-DD",
       "summary": "3行サマリ（決定事項・宿題含む）",
       "next_action": "次にやること",
       "confidence_hint": "上げ | 維持 | 下げ"
     },
     "tasks": [
       {"title": "タスク名", "due": "YYYY-MM-DD", "priority": "高|中|低"}
     ],
     "deal_update": {
       "confidence": 0.6,
       "status": "リード|初回商談|提案|見積|クロージング|受注|失注|保留",
       "next_action": "次アクション",
       "next_date": "YYYY-MM-DD",
       "last_contact": "商談日",
       "reason": "なぜ確度/ステータスをこう変えるかの根拠"
     }
   }
   ```
   - `confidence` は 0.0〜1.0（0.6=60%）。商談メモの「決裁者の関与・予算・競合・導入時期」から妥当な確度を**提案**する。
   - `deal_name` は既存案件名に合わせる（部分一致で解決される）。新規なら先にB（案件作成）。

2. **生成したJSONをユーザーに提示して承認を取る**（特に `deal_update` の確度・ステータス）。これが承認ポイント。勝手に反映しない。

3. 承認されたらJSONを一時ファイルに保存し実行：
   ```bash
   python src/process_meeting.py --client demo --input <path>.json --dry-run   # 念のため確認
   python src/process_meeting.py --client demo --input <path>.json             # 反映
   ```
   → 議事録登録・タスク展開・案件更新が一括反映。次回予定があれば `out/followup_*.json` が出る。

4. **カレンダー登録**：`out/followup_*.json` を読み、Google Calendar MCP（`mcp__c800f41e-...__create_event`）で予定を作成する。
   - Zoom/Meetリンクを付与（Youルール）。`addGoogleMeetUrl: true` か既存Zoom URLを `googleMeetUrl` に。
   - カレンダーは内容に応じて本業/個人事業を選ぶ（CLAUDE.mdの事業区分）。デフォルトは確認する。

5. 完了報告：登録した議事録・タスク・確度変化・カレンダー予定を要約して伝える。
6. **お礼メールの自動提案**：商談処理の直後、先方メールが登録されていれば（`email_context.py --deal <案件名>` で確認）、操作Gの手順でお礼メールの下書きを作成して提示する。先方メール未登録なら「先方メールを登録すればお礼メールも作れます」と一言添える。送信はしない。

---

## B. 案件作成
```bash
python src/new_deal.py --client demo --name "<案件名>" --company "<法人>" --status <ステータス> --confidence <0〜1> --amount <円> --next-action "<次アクション>" --last-contact <YYYY-MM-DD>
```
不明な引数は省略可。案件名は「取引先＋商材」で命名。
**法人（--company）**：このクライアントは2法人（`NITTA JAPAN`＝株式会社／`業務委託先A`＝合同会社）で案件を回している。どちらの法人の案件か不明なら必ずユーザーに確認してから作成する。

## C. レポート
```bash
python src/weekly_report.py --client demo                       # 全体（法人別内訳つき）
python src/weekly_report.py --client demo --company "業務委託先A"   # 法人で絞り込み
python src/weekly_report.py --client demo --slack               # Slackにも（SLACK_WEBHOOK_URL設定時）
```
出力（パイプライン期待値・法人別・ステージ別・停滞案件）をそのまま見やすく伝える。「NITTA JAPANの状況」等と言われたら --company で絞る。

## D. 案件更新（単発）
```bash
python src/update_deal.py --client demo --deal "<案件名>" --confidence <0〜1> --status <ステータス> --next-action "<…>" --next-date <YYYY-MM-DD> --last-contact <YYYY-MM-DD>
```
確度・ステータス変更は判断が絡むので、変更内容を一言確認してから実行する。

## E. クリーンアップ
```bash
python src/cleanup.py --client demo --keyword <キーワード>   # 議事録・タスクをアーカイブ
# 案件も対象にするなら --include-deals
```
削除系なので対象件数を伝えてから実行する。

---

## F. 連絡先登録（取引先＋先方メール）
```bash
python src/register_contact.py --client demo --deal "<案件名>" --company "<取引先名>" --email "<先方メール>" --contact "<担当者名>"
```
取引先DBに作成し、案件にリレーションで紐付ける。メールアドレスが分からなければユーザーに聞く。

## G. お礼メール下書き（商談後）
1. 連絡先＋文脈を取得：
   ```bash
   python src/email_context.py --client demo --deal "<案件名>"
   ```
   → 出力に `company`（法人）と `contact`（先方）が含まれる。`contact.email` が null なら先にF（連絡先登録）。
2. **法人別テンプレを読む**：`templates/email_templates.json` から、出力の `company`（NITTA JAPAN / 業務委託先A）に対応するエントリを使う。greeting/closing/署名/トーンをそれに合わせる。署名の `<...>` プレースホルダがまだ実値でない場合はその旨を一言添える。
3. Claudeがお礼メール文面を作成（商談内容・次アクションを踏まえ、法人のトーンと署名を適用）。
4. Gmail MCP `mcp__...__create_draft` で **下書きを作成**（to=先方メール）。
5. **送信はしない**。下書きを作った旨と本文を提示し、ユーザーが確認して送る。

## H. リマインドメール下書き（前日）
1. 翌日に予定がある案件を抽出：
   ```bash
   python src/email_context.py --client demo --due-in 1
   ```
2. 各案件についてClaudeがリマインド文面（日時・場所/Zoom・議題）を作成。**案件の `company` に応じて `templates/email_templates.json` の法人別署名・トーンを適用**。
3. Gmail MCPで下書き作成（to=先方メール）。**送信はしない**。
4. 何件分の下書きを作ったか報告。
   ※**毎朝の自動下書きは設定済み**：スケジュールタスク `case-reminder-drafts`（毎朝7:48頃）が `--due-in 1` を回し、翌日予定の案件にリマインド下書きを自動生成する（送信は手動）。手動で今すぐ作りたい時はこの操作Hを実行。

## ガードレール
- **メールは下書きまで。送信は必ずユーザーが実施**（勝手に送らない）。宛先は必ず取引先DBの登録アドレスのみ。
- `.env`のトークン値は読まない・表示しない・チャットに貼らない。
- 案件の確度/ステータス更新と削除は、実行前に必ずユーザー確認。
- 本業データと個人事業データを混在させない（クライアント=configを分ける）。
- スクリプト実行Bashは `dangerouslyDisableSandbox: true`（`.env`読み取りのため）。
- 詳細仕様は `workflow.md` / `README.md` を参照。
