---
name: competitive-research
description: ユーザーが売り出したいサービス・プロダクトの情報をもとに競合リサーチの初期調査を行い、企画会議や営業資料のたたき台となるMarkdownレポートとPowerPointスライドを同時生成する。「競合リサーチ」「競合調査」「競合分析」「市場調査」「competitor research」と言われたとき、または新しいサービス・プロダクトを展開する前の初期調査として自動的に起動する。
---

# competitive-research — 競合リサーチ初期調査スキル

ユーザーが入力したサービス・プロダクト情報をもとに、WebSearchで競合を調査し、
**Markdownレポート（.md）と PowerPointスライド（.pptx）を必ずセットで出力**するスキル。

---

## ゴール

- 新規サービス展開前の初期調査を完了させる
- 不足情報があっても調査を止めず、仮定を明記して進める
- 「要確認」を明示し、最終資料ではなくたたき台として使えるアウトプットを作る
- **Markdownレポートとスライドの2ファイルを必ずセットで保存する（どちらか片方だけは禁止）**
  - Markdown: `~/Desktop/YYYYMMDD_競合リサーチ_{service_slug}.md`
  - Slides:    `~/Desktop/YYYYMMDD_競合リサーチ_{service_slug}.pptx`

---

## 実行フロー

### Step 1: ヒアリング（AskUserQuestion で一括収集）

以下の情報を一度に聞く。**複数回に分けて聞かない。**

必須項目（なければ仮定して進める）:
1. サービス名またはプロダクト名
2. サービス概要（何をするサービスか、2〜3文）
3. 想定ターゲット（業種・規模・役職など）
4. 提供形態（SaaS / アプリ / コンサル / EC など）
5. 価格帯（目安でよい）
6. 現時点で考えている強み
7. 現時点で想定している競合（あれば）
8. 調査したい市場・地域（例：国内 / 日本のSMB / グローバルなど）

既にユーザーが情報を書いている場合はSkipし、そのまま Step 2 へ進む。

情報が一部欠けていても **止めない**。欠けた項目は仮定を置いて「分析上の仮定」に明記する。

---

### Step 2: WebSearch で競合リサーチ（必ず実行する）

以下のクエリパターンでWebSearchを行う。各クエリを**並列**で実行する。

#### 検索クエリ設計（サービス内容に合わせて変形する）

```
1. "{サービスカテゴリ} 競合 比較 {現在の年}"
2. "{サービスカテゴリ} SaaS 料金 機能比較"
3. "{ターゲット業種} {課題} ツール おすすめ"
4. "{競合候補名（ユーザー指定）} 料金 機能 評判"
5. "{サービスカテゴリ} market share Japan" （日本市場の場合）
   または "{service category} competitors {現在の年}" （グローバルの場合）
```

#### 検索で収集すべき情報

- 競合サービスの名前・運営会社
- 価格帯・プラン構成
- 主な機能・特徴
- ターゲット顧客層
- 強み・弱み（レビューサイト・比較記事から）
- 導入実績・ユーザー数（公式発表があれば）
- 最近の動向（プレスリリース・資金調達など）

#### 注意事項

- 断定しすぎない。価格・機能は「要確認」として扱う
- 架空の情報を作らない
- 検索結果に情報がなければ「情報なし / 要確認」と記載する

---

### Step 3: 分析・整理

収集した情報をもとに、以下の順で分析する。

1. 競合カテゴリの分類（直接競合 / 間接競合 / 代替手段 / 周辺サービス）
2. 比較軸の設計（価格・機能・導入しやすさ・サポート・対象顧客・専門性・拡張性・実績）
3. 差別化ポイントの抽出（ユーザーのサービスが勝てる軸を現実的に特定）
4. 勝てるポジションの整理
5. スライド10枚分の本文案の作成

---

### Step 4: Markdownレポート生成・保存

以下のMarkdown形式でレポートを作成し、ファイルに保存する。

保存先: `~/Desktop/YYYYMMDD_競合リサーチ_{service_slug}.md`
- YYYYMMDD は今日の日付
- service_slug はサービス名をローマ字またはアルファベットにしたもの（スペースはハイフン）

Markdownを保存したら、**必ず Step 5 のスライド生成へ進む（省略禁止）**。

---

### Step 5: PowerPointスライド生成・保存（必須）

**Markdownレポートとセットで必ずスライドを生成する。**
スライドはBashツールでPythonスクリプトを実行して生成する。

#### 使用するカラーパレット（slide-creator と統一）

```python
C_P900 = RGBColor(0x0B, 0x41, 0x6E)  # primary-900（濃色背景）
C_P700 = RGBColor(0x02, 0x5B, 0xA1)  # primary-700
C_A500 = RGBColor(0x14, 0xB8, 0xA6)  # accent-500（アクセント）
C_A100 = RGBColor(0xCC, 0xFB, 0xF6)  # accent-100（ハイライト背景）
C_N900 = RGBColor(0x17, 0x17, 0x17)  # neutral-900（本文）
C_N600 = RGBColor(0x52, 0x52, 0x52)  # neutral-600（サブ）
C_N300 = RGBColor(0xD4, 0xD4, 0xD4)  # neutral-300（罫線）
C_N50  = RGBColor(0xFA, 0xFA, 0xFA)  # neutral-50（カード背景）
C_WH   = RGBColor(0xFF, 0xFF, 0xFF)  # white
```

#### フォント

- 日本語: `"Hiragino Sans"`（macOS）/ `"Yu Gothic"`（Windows）
- 数字・英語: `"Arial"`

#### スライドサイズ

`13.333 × 7.5 inch`（16:9）

#### スライド構成（10枚固定）

| # | パターン | タイトル |
|---|---|---|
| 1 | title（濃色背景） | 表紙：サービス名・日付・ステータス |
| 2 | stat-hero + bullets | 市場背景：数字ハイライト + 4点の状況説明 |
| 3 | 3カラムカード | 顧客課題：3分類をカードで並列表示 |
| 4 | 4象限カード | 競合カテゴリ：4カテゴリの整理 |
| 5 | テーブル | 主要競合比較：5〜7社の比較表 |
| 6 | bullets（アイコン付き） | 差別化ポイント：4〜5点を列挙 |
| 7 | 左右2カラム | 勝てるポジション：ターゲット像 + 訴求 |
| 8 | 3カラムプランカード | 提供プラン：Lite / Standard / Pro |
| 9 | process（5ステップ） | 導入フロー：ステップカード横並び |
| 10 | CTA（濃色背景） | 次のアクション：3ボックスで行動提示 |

#### Pythonスクリプトの雛形（毎回内容に合わせて書き起こす）

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# カラー定数（上記パレット）
# ...

def blank_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def set_bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color

def add_rect(slide, l, t, w, h, fill=None, line_c=None, lw=None):
    sh = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line_c:
        sh.line.color.rgb = line_c
        if lw:
            sh.line.width = Pt(lw)
    else:
        sh.line.fill.background()
    return sh

def add_txt(slide, text, l, t, w, h, size, bold=False, color=C_N900,
            align=PP_ALIGN.LEFT, font=None):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(text.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = font or "Hiragino Sans"
    return tb

def add_heading(slide, text, dark=False):
    c = C_WH if dark else C_N900
    add_txt(slide, text, 0.55, 0.3, 12.2, 0.65, 24, bold=True, color=c)
    add_rect(slide, 0.55, 0.98, 0.6, 0.055, fill=C_A500)

# 各スライドの生成関数（s01〜s10）を内容に合わせて実装する
# ...

def main():
    prs = Presentation()
    prs.slide_width  = Inches(13.333)
    prs.slide_height = Inches(7.5)
    # 各スライド関数を呼び出す
    out = "/Users/you/Desktop/YYYYMMDD_競合リサーチ_slug.pptx"
    prs.save(out)
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()
```

スクリプトは `$TMPDIR/build_competitive_slides.py` に書き出し、Bashで実行する。
実行後、生成されたファイルのフルパスをユーザーに報告する。

#### スライド生成のルール

- 絵文字を一切入れない（テキスト内の Unicode emoji 禁止）
- グラデーション禁止（濃色背景スライドの上下グラデのみ例外）
- 1スライドに詰め込みすぎない（テキスト密度は7割以下を目安）
- アクセント色（C_A500）は1スライドにつき1〜2箇所まで
- 比較表は「要確認」を必ず含める

---

## 出力フォーマット：Markdownレポート（必ずこの構造で出力）

```markdown
# 競合リサーチ資料
**対象サービス**: {サービス名}
**作成日**: {YYYY-MM-DD}
**ステータス**: 初期調査たたき台（最終資料ではありません）

---

## 1. 対象サービス・プロダクトの整理

| 項目 | 内容 |
|---|---|
| サービス名 | |
| 概要 | |
| 想定ターゲット | |
| 解決する課題 | |
| 提供形態 | |
| 想定価格帯 | |
| 現時点の強み | |
| 分析上の仮定 | |

## 2. 顧客課題の整理

| 分類 | 課題 |
|---|---|
| 業務上の課題 | |
| コスト面の課題 | |
| 導入・運用面の課題 | |

## 3. 競合カテゴリの分類

| カテゴリ | 内容 | 代表的な競合・代替手段 |
|---|---|---|
| 直接競合 | | |
| 間接競合 | | |
| 代替手段 | | |
| 周辺サービス | | |

## 4. 競合比較軸

| 比較軸 | 見るべき理由 |
|---|---|
| 価格 | |
| 機能 | |
| 導入しやすさ | |
| サポート体制 | |
| 対象顧客 | |
| 専門性 | |
| 拡張性 | |
| 実績 | |

（サービス内容に合わせた独自の比較軸も追加する）

## 5. 主要競合の比較表

| 競合名 | カテゴリ | 主な特徴 | 強み | 弱み・制約 | 価格情報 | 要確認事項 |
|---|---|---|---|---|---|---|
| | | | | | | |

## 6. 自社サービスの差別化ポイント

| 観点 | 差別化ポイント |
|---|---|
| ターゲット | |
| 価格 | |
| 導入しやすさ | |
| 専門性 | |
| サポート | |
| 継続利用 | |
| その他 | |

## 7. 勝てそうなポジション

- **狙うべき顧客層**:
- **刺さりやすい訴求**:
- **避けるべき競争軸**:
- **最初に検証すべき市場**:
- **初期導入先として相性が良い顧客**:

## 8. スライド構成案

| スライド番号 | タイトル | 内容 |
|---|---|---|
| 1 | 表紙 | |
| 2 | 市場背景 | |
| 3 | 顧客課題 | |
| 4 | 競合カテゴリ整理 | |
| 5 | 主要競合比較 | |
| 6 | 自社サービスの差別化 | |
| 7 | 勝てるポジション | |
| 8 | 提供プラン | |
| 9 | 導入イメージ | |
| 10 | 次のアクション | |

## 9. スライド本文案

（各スライドの見出し1つ + 本文3〜5行）

### スライド1: 表紙
...

（以下同様に全10スライド分）

## 10. 人間が追加で確認すべき項目

| 確認項目 | 確認先 |
|---|---|
| 最新価格 | 公式料金ページ |
| 機能詳細 | 公式サイト・資料請求 |
| 導入実績 | 導入事例・プレスリリース |
| 法規制・業界ルール | 公的機関・専門家 |
| 顧客ニーズ | ヒアリング・アンケート |
| 競合の更新情報 | 公式ニュース・リリース |

---

> このレポートは初期調査のたたき台です。最終的な意思決定の前に上記の確認事項を検証してください。
```

---

## 分析ルール（必ず守る）

| ルール | 詳細 |
|---|---|
| 断定しない | 価格・機能・実績は変化するため「〜と見られる」「要確認」で扱う |
| 架空情報NG | 不明な情報は「情報なし」「要確認」と明記。作り話をしない |
| 競合を悪く書かない | 弱点は「制約」「対応範囲外」等の中立表現で記載 |
| 自社を過剰に持ち上げない | 差別化は現実的・具体的な軸で表現する |
| 仮定は明記 | 不足情報を補った仮定はセクション1の「分析上の仮定」に列挙 |
| たたき台として提供 | 「初期調査資料」であることをレポート冒頭に必ず明記 |

---

## やってはいけないこと

- WebSearchをスキップして仮定だけで競合を列挙する
- 競合情報を1件も収集せずにレポートを出す
- 1回のWebSearchだけで済ませる（最低3〜5クエリ実行する）
- 実在しない競合サービスを列挙する
- 価格を断定する（「〜円です」→「〜円程度（要確認）」）
- Markdownレポートだけ出してスライドを省略する（必ず両方出力する）
- スライドをチャット上のテキストだけで表現して.pptxを生成しない

---

## 参考: ファイル構成

```
~/.claude/skills/competitive-research/
└── SKILL.md   # このファイル
```
