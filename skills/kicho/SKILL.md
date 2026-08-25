---
name: kicho
description: エクセル簿記（青色申告の複式帳簿）への自動記帳。「記帳して」「仕訳入れて」「帳簿つけて」「経費入れて」「今月の定型仕訳」と言われたとき、レシート・明細・取引内容を渡されて帳簿への記録を頼まれたときに起動する。CSVを生成してdry-runで確認後、AppleScript経由でR8年.xlsの仕訳帳に追記する。
---

# エクセル簿記 自動記帳スキル

ツール本体: `~/projects/tools/excelb-kicho/`（詳細はREADME.md）
対象帳簿: `/Users/you/Library/Mobile Documents/com~apple~CloudDocs/Desktop/個人事業用/excelb-mac/R8年.xls`

## 手順

1. **仕訳の組み立て**: ユーザーの依頼（自然言語・レシート画像・CSV明細）から仕訳CSVを作る
   - フォーマット: `date,debit_code,amount,credit_code,memo`（date=YYYY-MM-DD、金額=整数円）
   - 科目コードは `~/projects/tools/excelb-kicho/accounts.json` で必ず確認する
   - 経費支払いは原則 貸方102（当座預金）。現金なら101、プライベート口座・個人クレカ立替なら172（事業主借）
   - 売上入金は 借方102 / 貸方1
   - 判断に迷う科目（按分割合・事業関連性）は勝手に決めずユーザーに確認する
2. **月次定型仕訳**の依頼なら: `python3 ~/projects/tools/excelb-kicho/monthly.py YYYY-MM -o /tmp/kicho.csv`
   - 定型の追加・変更を頼まれたら `recurring.json` を編集
3. **dry-runで提示**: `python3 ~/projects/tools/excelb-kicho/add_entries.py <csv> --dry-run` の結果をユーザーに見せて承認を得る
4. **書き込み**: 承認後に `python3 add_entries.py <csv>` を実行（Excelが起動する。sandboxはApple Eventsをブロックするため無効化が必要）
   - 帳簿ファイルをExcelで開いたままにしないよう事前に注意する
5. **報告**: 読み戻し検証結果と、バックアップファイルのパスを報告する

## 過去の仕訳パターン（摘要の書き方の参考）

- 通信費60%事業利用（毎月15日・6,000円 ※金額は例）/ 自宅家賃30%事業利用(毎月15日・30,000円 ※金額は例)
- Render利用料(毎月25日・2,100円)/ 公式LINE利用料(毎月25日・5,500円)
- 月末の海外サブスク: 摘要に「150円換算」のように為替レートを記載
- 売上入金は摘要空欄が多い

## 注意

- 年をまたぐ仕訳（1月に前年12月分）は対象ファイルが違う可能性があるためユーザーに確認
- 医療・本業関連の支出はこの帳簿（個人事業）に入れない
