---
name: py-worktree
description: Pythonプロジェクトの複数ファイルを横断して一括改修するとき、git worktreeで作業を隔離する。「一括修正」「一括置換」「一括リネーム」「まとめてリファクタ」「全部のファイルを直して」「移行して」「マイグレーション」と言われたとき、または3ファイル以上のPythonファイルを横断して書き換える作業に着手する前に起動する。本体ディレクトリを汚さずに作業し、差分を確認してからマージする。未Git管理のプロジェクトはその場でgit initする。
---

# py-worktree — 一括改修の隔離

スクリプト: `~/.claude/skills/py-worktree/scripts/wt.sh`

## 発火する条件（すべて満たすとき）

1. **Pythonが主体**のプロジェクト（`~/projects/tools/`・`~/projects/scripts/`・`~/projects/labs/` 配下が中心）
2. **3ファイル以上を横断**して書き換える（一括置換・リネーム・API変更・ディレクトリ再編・依存の入れ替え）
3. **途中で止まると中途半端な状態が残る**変更

## 発火させない条件（どれか1つでも当たれば通常どおり直接編集する）

- 1〜2ファイルだけの修正、バグ1件の修正、読み取り・調査のみ
- Next.js等の**JSプロジェクト**（`node_modules` の再インストールが必要でコストに合わない。standby-tech-hp・standby-post は対象外）
- `.venv` が数百MB級で、かつリンク共有が壊れる構成
- ユーザーが「そのまま直して」と明示したとき

判断に迷ったら**隔離せず直接編集**を選ぶ。worktreeは手数が増えるので、割に合うときだけ使う。

## 手順

1. **発火条件を判定**し、隔離する旨を一行でユーザーに伝える（許可は求めない。ただし未Git管理なら手順2で必ず止まる）

2. **Git管理の確認**
   ```bash
   ~/.claude/skills/py-worktree/scripts/wt.sh init <repoパス>
   ```
   - すでにGit管理下なら何もせず抜ける
   - 未Git管理なら `.gitignore` を作って `git init` + `git add` まで実行し、**コミット対象の一覧・5MB超のファイル・機密の疑いがあるファイル**を表示して止まる
   - この一覧を**必ずユーザーに見せて承認を取ってから**初回コミットする。`.env` や鍵ファイルが混ざっていたら `.gitignore` を直して `git reset` からやり直す

3. **worktreeを作る**（slugはケバブケースで内容がわかる名前）
   ```bash
   ~/.claude/skills/py-worktree/scripts/wt.sh new <repoパス> <slug>
   ```
   `<repo>/.worktrees/<slug>/` が作業場所。`.venv`・`.env` は本体からシンボリックリンクで共有される（再インストール不要）

4. **worktree内で改修する**。以後の編集・実行はすべて `<repo>/.worktrees/<slug>/` 側で行う。本体は触らない

5. **動作確認**をworktree内で行う（テスト・スクリプト実行）。壊れていたらここで直す

6. **差分を見せる**
   ```bash
   ~/.claude/skills/py-worktree/scripts/wt.sh diff <repoパス> <slug>
   ```
   変更ファイル数と内容をユーザーに報告する

7. **コミットしてマージ**（承認後）
   ```bash
   git -C <repo>/.worktrees/<slug> add -A && git -C <repo>/.worktrees/<slug> commit -m "<メッセージ>"
   ~/.claude/skills/py-worktree/scripts/wt.sh finish <repoパス> <slug>
   ```
   本体へマージし、worktreeとブランチを自動で片付ける

8. **やめる場合**は `wt.sh abort <repoパス> <slug>`（破棄内容を表示してy/N確認）

## 守ること

- **本体側に未コミットの変更があると `finish` は失敗する**。先に本体を整理する
- worktreeを作ったまま放置しない。終わったら必ず `finish` か `abort` を通す（残骸がディスクを食う）
- `wt.sh list` / `wt.sh clean` で残骸を点検できる
- コミットメッセージは Conventional Commits 形式
