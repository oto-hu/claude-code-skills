---
name: video-edit
description: 動画ファイルから無音部分をカットして書き出す。「無音カット」「動画編集」「silence cut」「サイレントカット」と言われたとき、または動画ファイルパスを渡して編集を依頼されたときに使う。ffmpegを使ってローカルで完結する。
---

# video-edit スキル

動画の無音部分をカットして新しいファイルとして書き出す。ffmpeg がインストールされていること前提（`which ffmpeg` で確認）。

## 使い方

```
/video-edit /path/to/input.mp4
/video-edit /path/to/input.mp4 --threshold -35dB --padding 0.3
```

`args` に動画ファイルのパスが渡される。オプションが省略された場合はデフォルト値を使う。

## 実行手順

### 1. 入力確認

- ファイルが存在するか確認する（`ls` で確認）
- 拡張子が動画形式（mp4, mov, mkv, avi, webm）かチェック
- ffmpeg が使えるか確認（`which ffmpeg`）

### 2. パラメータ整理

| パラメータ | デフォルト | 説明 |
|-----------|-----------|------|
| `--threshold` | `-35dB` | 無音と判定する音量の閾値。小さいほど静かな部分のみカット |
| `--min-silence` | `0.5` | 無音と判定する最小時間（秒）。短いと息継ぎもカットされる |
| `--padding` | `0.2` | カット前後に残すバッファ（秒）。0だと話し始めが切れやすい |

ユーザーがパラメータを指定した場合はそちらを優先する。

### 3. 無音区間の検出

ffmpeg の `silencedetect` フィルターで無音区間を取得する：

```bash
ffmpeg -i input.mp4 -af "silencedetect=noise=-35dB:d=0.5" -f null - 2>&1
```

出力から `silence_start` と `silence_end` の行を抽出してリスト化する。

### 4. 有音区間の計算

無音区間の逆（有音区間）を計算する。padding を適用して前後に余白を持たせる：

```
有音区間 = [silence_end[i] + padding, silence_start[i+1] - padding]
```

ファイル先頭（0秒）〜最初の無音開始、および最後の無音終了〜ファイル末尾も有音区間に含める。

### 5. セグメントの切り出しと結合

有音区間ごとに一時ファイルとして切り出し、concat で結合する：

```bash
# 各セグメントを切り出し
ffmpeg -i input.mp4 -ss {start} -to {end} -c copy /tmp/segment_000.mp4

# concat リストファイルを作成
echo "file '/tmp/segment_000.mp4'" >> /tmp/concat_list.txt
...

# 結合
ffmpeg -f concat -safe 0 -i /tmp/concat_list.txt -c copy output_cut.mp4
```

### 6. 後処理

- 一時ファイルをすべて削除する（`rm /tmp/segment_*.mp4 /tmp/concat_list.txt`）
- 出力ファイルのパスを絶対パスで報告する
- 元の動画の長さと、カット後の長さを秒単位で比較して報告する

## 出力ファイル名のルール

入力ファイルと同じディレクトリに保存する：
- 入力: `/path/to/video.mp4`
- 出力: `/path/to/video_cut.mp4`

既に `_cut.mp4` が存在する場合は `_cut2.mp4`、`_cut3.mp4` と連番にする。

## エラーハンドリング

- ファイルが見つからない → パスを確認してもらうメッセージを出す
- 無音区間が0件 → 「無音が検出されませんでした。閾値（--threshold）を上げてみてください」と伝える
- ffmpeg が見つからない → `brew install ffmpeg` を案内する
- 有音区間が短すぎる（合計1秒未満）→ 「ほぼ全体が無音です。threshold を確認してください」と警告する

## 実行後の報告フォーマット

```
無音カット完了

入力:  /path/to/video.mp4（元の長さ: XX秒）
出力:  /path/to/video_cut.mp4（カット後: XX秒）
削減:  XX秒カット（XX%短縮）

検出した無音区間: XX箇所
```
