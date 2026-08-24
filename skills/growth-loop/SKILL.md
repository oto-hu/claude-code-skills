---
name: growth-loop
description: Standby Tech（個人事業）のHP・note・SNSのCTR/CVRを計測し、自動で改善実験を回すループ。「CTR」「CVR」「流入改善」「growth loop」「グロースループ」「効果測定して改善して」と言われたとき、および毎週月曜の定期実行時に起動する。GSC/GA4から数値を取り、ファネルの壊れている層を特定し、CTR層のみ自動でtitle/descriptionを書き換えてデプロイする。SNS・noteは計測と改善案提示まで。
---

# growth-loop

「投稿しておしまい」を「測って直し続ける」に変えるためのループ。

## 最初に必ず読むファイル（この順に）

1. `/Users/you/projects/standby/growth-loop/loop.md` — 判定基準（ファネルの層・閾値・サーキットブレーカー）
2. `/Users/you/projects/standby/growth-loop/experiments.md` — 実験台帳（**唯一の状態**）
3. `/Users/you/projects/standby/growth-loop/gate.yaml` — 触ってよい範囲

**この3ファイルが正。以下の手順はその補足にすぎない。** 矛盾したら上記が優先。

## 対象

- HP：https://www.stand-bytech.com/（GSC siteUrl も同じ）
- GA4 プロパティ：`000000000`（Standby Tech）
- note：https://note.com/standby_tech
- Instagram / Threads：Standby Tech 名義

**本業は対象外。** 一切扱わない。

---

## 手順

### STEP 1. 台帳を読む

`experiments.md` を読み、**判定日を過ぎた `running` の実験**を全て拾う。ここが起点。
施策ごとに一回限りタスクを作る運用は廃止した。判定はすべてこのループが引き受ける。

### STEP 2. 数値を集める

MCPで直接取る（収集用スクリプトは不要）。

**GSC**（`mcp__gsc__search_analytics` / `enhanced_search_analytics`）
siteUrl は `https://www.stand-bytech.com/`、期間は実行日の前日から28日前まで。

1. `dimensions=page` — ページ別の 表示/クリック/CTR/平均順位
2. `dimensions=query`（rowLimit 200）
3. `dimensions=query,page`（rowLimit 1000）— **カニバリ確認。これを省略しない**
   （2026-08-06に、ブログだけ見て「line 自動化」の8割を持つサービスページを見落とした前例がある）
4. `mcp__gsc__detect_quick_wins`（minImpressions=10, positionRangeMin=4, positionRangeMax=40）

**GA4**（`mcp__google-analytics__run_report`、property `000000000`）

- ディメンション `sessionSource`, `sessionMedium`, `sessionCampaignName`
- 流入元別のセッション数と `/ai-assessment` の到達・完了
- UTM設計：IGは bio→`/links`（`utm_source=instagram&utm_medium=bio`）、Threadsは `?src=threads`

**Instagram / Threads**

```bash
cd /Users/you/projects/standby/growth-loop && .venv/bin/python scripts/collect_instagram.py --days 7
```

```bash
cd /Users/you/projects/standby/growth-loop && .venv/bin/python scripts/collect_threads.py --days 7
```

> `threads-automation/fetch_thread_insights.py` は使わない。あれは環境変数のみを読むため
> スケジュール実行から取得できない（2026-08-09に実際に「未入力」で持ち越しになった）。
> `collect_threads.py` は growth-loop/.env を読み、アカウント照合も行う。

> **Threadsのリンククリック数はAPIで取得できない。** `loop.md` §4 の判定には
> GA4 の `?src=threads` 流入セッション数を使うこと。

**note（2アカウント）**

```bash
cd /Users/you/projects/standby/growth-loop && .venv/bin/python scripts/collect_note.py
```

`gate.yaml` の `accounts` に定義された2アカウントを順に回し、
`data/YYYY-MM-DD_note_<handle>.json` に保存する。**取得のみで投稿・編集は一切しない。**

> **ブラウザのウィンドウが表示される。** noteはヘッドレスだとログインを弾くため（2026-08-09実測）、
> 既定でブラウザを起動する。これは正常な挙動なので閉じずに待つこと。

> スクリプトはログイン直後にアカウントIDを照合し、`gate.yaml` の `handle` と違えば
> **記事データを一切読まずに終了コード2で中断する**。
> （2026-08-05に自社記事を委託先アカウント weel_media へ誤公開した事故があるため、読み取りでも省略しない）
> 中断したら回避せず、ユーザーに「どのアカウントでログインされていたか」を報告する。

**2つのnoteを合算しない**（`loop.md` §4）。導線が別なので混ぜると判断を誤る。

| アカウント | 送客先 |
|---|---|
| `standby_tech` | HP `/ai-assessment` ← Standby Techの集客成果はこちらだけ |
| `python_poikatsu`（表示名 python_man） | Amazonアフィリエイト。HPへの送客は目的ではない |

**noteの `views` / `likes` は累計値。そのまま週次実績として報告しない。**
先週の同名ファイルとの差分を取る。先週分が無ければ「基準取得のみ・未測定」と記録する。

記事→HPへの流入は GA4 の `sessionSource=note` で見る（こちらは期間指定なので差分不要）。

ブラウザを手で操作して読みに行かないこと。アカウント照合を通らない経路を作らないため。

**取得できなかった数値は「未入力」と記録する。推測で埋めることは絶対にしない。**

### STEP 3. ファネルの層を特定する

`loop.md` §1 の判定順に従い、**壊れている層を1つだけ**特定する。上から見て最初に該当した層を扱う。

- 28日表示 < 100 → L1（表示不足）。CTR/CVRを論じない
- 表示 >= 100 かつ CTR < 1.0% → **L2。自動改善の対象**
- CTR >= 1.0% かつ 診断到達 < 5% → L3/L4。人間へエスカレーション
- どれでもない → 健全。触らない

### STEP 4. 判定待ちの実験を判定する

`loop.md` §2 の表に従う。**CTRで判定する。順位で判定しない。**

- 成功：CTR 1.5倍以上 かつ クリック +2件以上
- 変化なし：それ未満 → 失敗カウント +1
- 悪化：CTRが実施前を下回る → **即ロールバック**

```bash
cd /Users/you/projects/standby/growth-loop && .venv/bin/python scripts/apply_title_rewrite.py --rollback latest
```

表示回数が増えていてもクリック0なら**失敗**。表示増を成功と読み替えない。

**サーキットブレーカー**：同一URLで3回連続改善なし → `circuit_open` にして自動対象から外し、
そのクエリの上位3件を実際に確認したうえで「記事の切り口自体を変える」提案を人間に出す。
**4回目のタイトル変更をしない。**

### STEP 5. 新しい実験を起票して実行する（CTR層のみ自動）

開始条件（`loop.md` §2、すべて満たすこと）を確認してから、最大3件。

1. 変更案を作る
   - GSC `query,page` でその記事が**実際に受けているクエリ**の語を必ず使う。想像で書かない
   - 数字・具体値を前方に。title 全角30字以内、description 全角60字以内
2. 変更指示JSONを書く（スクラッチパッドへ）

```json
[{"slug": "poc-development-cost", "title": "...", "description": "..."}]
```

3. 確認 → 適用

```bash
cd /Users/you/projects/standby/growth-loop
.venv/bin/python scripts/apply_title_rewrite.py --changes <path>          # 確認のみ
.venv/bin/python scripts/apply_title_rewrite.py --changes <path> --apply  # 適用
```

ゲート違反は必ずスクリプトが弾く。**エラーが出たら回避せず、指摘どおり案を作り直す。**
gate.yaml を緩めて通そうとしないこと。

4. デプロイ（ビルドが通った場合のみ main へマージ・push）

```bash
cd /Users/you/projects/standby/growth-loop && ./scripts/deploy.sh "EXP-0XX CTR: <slug> のtitle短縮"
```

> このスクリプトは push を含むため、**Bashツールから `dangerouslyDisableSandbox: true` で実行する**。
> 実行後は転送ログ（`To https://github.com/...`）が出ているかで成否を判定する。
> ログが無ければ push できていない。成功したと書かないこと。

5. `experiments.md` に `running` で追記する（ID・仮説・変更内容・実施日・ベースライン・判定日=28日後）

### STEP 6. 記録して報告する

`experiments.md` を更新する：判定結果・サーキットブレーカーのカウント・**学びを1行**。
学びが書けないなら判定していないのと同じ。

ユーザーへの報告は簡潔に。長い分析を書かない。

- 判定した実験の結果（表1つ）
- 今週開始した実験（あれば）
- 診断コンプリート数（今週／累計）と流入元別の内訳
- **人間の判断が必要な事項**（あれば。無ければ「なし」）

---

## やらないこと

- 新規記事を書く、SNS・noteへ投稿する（人間の判断）
- `lib/serviceContent.ts`（サービスページ）を触る
- 数値が無い状態で判定する・推測で埋める
- 1つのURLで同時に2つ以上の実験を走らせる
- gate.yaml を自分で書き換えて制約を緩める
- 本業に関する一切
