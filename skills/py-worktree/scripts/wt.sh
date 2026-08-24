#!/usr/bin/env bash
# py-worktree — 軽量Pythonプロジェクトの一括改修を worktree で隔離する
# 使い方: wt.sh <サブコマンド> [引数]
set -euo pipefail

WT_DIR_NAME=".worktrees"

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "  $*"; }

# リポジトリルートを解決する（引数が無ければカレント）
resolve_repo() {
  local p="${1:-$PWD}"
  [ -d "$p" ] || die "ディレクトリが存在しない: $p"
  git -C "$p" rev-parse --show-toplevel 2>/dev/null || die "Git管理されていない: $p（先に 'wt.sh init $p' を実行）"
}

wt_path() { echo "$1/$WT_DIR_NAME/$2"; }
wt_branch() { echo "wt/$1"; }

# ---------------------------------------------------------------- init
cmd_init() {
  local repo="${1:-$PWD}"
  [ -d "$repo" ] || die "ディレクトリが存在しない: $repo"
  repo="$(cd "$repo" && pwd)"
  if git -C "$repo" rev-parse --show-toplevel >/dev/null 2>&1; then
    info "すでにGit管理下: $(git -C "$repo" rev-parse --show-toplevel)"
    return 0
  fi

  if [ ! -f "$repo/.gitignore" ]; then
    cat > "$repo/.gitignore" <<'GI'
__pycache__/
*.py[cod]
.venv/
venv/
.env
.env.*
!.env.example
*.egg-info/
.pytest_cache/
.mypy_cache/
.ipynb_checkpoints/
.DS_Store
.worktrees/
*.log
GI
    info ".gitignore を作成した"
  else
    grep -q '^\.worktrees/' "$repo/.gitignore" || echo '.worktrees/' >> "$repo/.gitignore"
    grep -q '^\.env$' "$repo/.gitignore" || echo '.env' >> "$repo/.gitignore"
    info ".gitignore に .worktrees/ と .env を追記した（既存は保持）"
  fi

  git -C "$repo" init -q
  git -C "$repo" add -A

  # --- 初回コミット前の安全確認 ---
  local n big secrets
  n=$(git -C "$repo" diff --cached --name-only | wc -l | tr -d ' ')
  big=$(git -C "$repo" diff --cached --name-only | while read -r f; do find "$repo/$f" -type f -size +5M 2>/dev/null; done || true)
  secrets=$(git -C "$repo" diff --cached --name-only | grep -Ei '\.env|secret|credential|password|\.pem$|\.key$' || true)

  echo
  echo "=== 初回コミット対象: ${n} ファイル ==="
  git -C "$repo" diff --cached --name-only | head -30
  [ "$n" -gt 30 ] && echo "  ...他 $((n-30)) ファイル"
  if [ -n "$big" ]; then echo; echo "!! 5MB超のファイル:"; echo "$big"; fi
  if [ -n "$secrets" ]; then echo; echo "!! 機密の疑いがあるファイル:"; echo "$secrets"; fi
  echo
  echo "問題なければ次を実行:"
  echo "  git -C \"$repo\" commit -m 'chore: 初回コミット'"
  echo "（機密・巨大ファイルがある場合は .gitignore を直して 'git -C \"$repo\" reset' からやり直す）"
}

# ---------------------------------------------------------------- new
cmd_new() {
  local repo slug
  repo="$(resolve_repo "${1:?repoパスを指定}")"
  slug="${2:?作業名（スラッグ）を指定}"
  local path branch
  path="$(wt_path "$repo" "$slug")"
  branch="$(wt_branch "$slug")"

  [ -e "$path" ] && die "すでに存在する: $path"
  git -C "$repo" rev-parse --verify "$branch" >/dev/null 2>&1 && die "ブランチが既にある: $branch"

  mkdir -p "$repo/$WT_DIR_NAME"
  grep -qx "$WT_DIR_NAME/" "$repo/.git/info/exclude" 2>/dev/null || echo "$WT_DIR_NAME/" >> "$repo/.git/info/exclude"

  git -C "$repo" worktree add -q -b "$branch" "$path"
  info "worktree作成: $path （ブランチ $branch）"

  # .venv / .env は追跡外なのでシンボリックリンクで共有する
  # 末尾スラッシュ付きの .gitignore 規則（.venv/ 等）はシンボリックリンクに一致しないため、
  # リンク名を info/exclude にも登録して未追跡扱いになるのを防ぐ
  for shared in .venv venv .env; do
    if [ -e "$repo/$shared" ] && [ ! -e "$path/$shared" ]; then
      ln -s "$repo/$shared" "$path/$shared"
      grep -qx "/$shared" "$repo/.git/info/exclude" 2>/dev/null || echo "/$shared" >> "$repo/.git/info/exclude"
      info "共有リンク: $shared"
    fi
  done

  echo
  echo "作業ディレクトリ: $path"
  echo "終わったら: wt.sh diff $repo $slug → wt.sh finish $repo $slug"
}

# ---------------------------------------------------------------- diff
cmd_diff() {
  local repo slug path branch base
  repo="$(resolve_repo "${1:?repoパスを指定}")"
  slug="${2:?作業名を指定}"
  path="$(wt_path "$repo" "$slug")"
  branch="$(wt_branch "$slug")"
  [ -d "$path" ] || die "worktreeが無い: $path"

  base="$(git -C "$repo" rev-parse --abbrev-ref HEAD)"
  echo "=== 未コミットの変更 ==="
  git -C "$path" status --short
  echo
  echo "=== $base との差分（コミット済み分） ==="
  git -C "$repo" diff --stat "$base...$branch" || true
}

# ---------------------------------------------------------------- finish
cmd_finish() {
  local repo slug path branch base
  repo="$(resolve_repo "${1:?repoパスを指定}")"
  slug="${2:?作業名を指定}"
  path="$(wt_path "$repo" "$slug")"
  branch="$(wt_branch "$slug")"
  [ -d "$path" ] || die "worktreeが無い: $path"

  [ -n "$(git -C "$path" status --porcelain)" ] && \
    die "worktree側に未コミットの変更がある。先にコミットすること: git -C \"$path\" add -A && git -C \"$path\" commit"
  [ -n "$(git -C "$repo" status --porcelain)" ] && \
    die "本体側に未コミットの変更がある。マージ前に整理すること"

  base="$(git -C "$repo" rev-parse --abbrev-ref HEAD)"
  git -C "$repo" merge --no-ff -m "merge: $slug" "$branch"
  info "$base に $branch をマージした"

  git -C "$repo" worktree remove "$path"
  git -C "$repo" branch -d "$branch"
  rmdir "$repo/$WT_DIR_NAME" 2>/dev/null && info "空になった $WT_DIR_NAME を削除した" || true
  info "worktreeとブランチを削除した"
}

# ---------------------------------------------------------------- abort
cmd_abort() {
  local repo slug path branch
  repo="$(resolve_repo "${1:?repoパスを指定}")"
  slug="${2:?作業名を指定}"
  path="$(wt_path "$repo" "$slug")"
  branch="$(wt_branch "$slug")"

  echo "!! 破棄する内容:"
  [ -d "$path" ] && git -C "$path" status --short
  git -C "$repo" log --oneline "$branch" -5 2>/dev/null || true
  echo
  read -r -p "本当に破棄する？ [y/N] " ans
  [ "$ans" = "y" ] || { echo "中止した"; return 1; }

  [ -d "$path" ] && git -C "$repo" worktree remove --force "$path"
  git -C "$repo" branch -D "$branch" 2>/dev/null || true
  rmdir "$repo/$WT_DIR_NAME" 2>/dev/null || true
  info "破棄した"
}

# ---------------------------------------------------------------- list / clean
cmd_list() {
  local repo; repo="$(resolve_repo "${1:-$PWD}")"
  git -C "$repo" worktree list
}
cmd_clean() {
  local repo; repo="$(resolve_repo "${1:-$PWD}")"
  git -C "$repo" worktree prune -v
  info "壊れた登録を整理した（ディレクトリ実体は消していない）"
}

case "${1:-}" in
  init)   shift; cmd_init "$@" ;;
  new)    shift; cmd_new "$@" ;;
  diff)   shift; cmd_diff "$@" ;;
  finish) shift; cmd_finish "$@" ;;
  abort)  shift; cmd_abort "$@" ;;
  list)   shift; cmd_list "$@" ;;
  clean)  shift; cmd_clean "$@" ;;
  *) cat <<'USAGE'
py-worktree — Pythonプロジェクトの一括改修を隔離する

  wt.sh init   <repo>              未Git管理なら .gitignore を作って git init（コミットは手動）
  wt.sh new    <repo> <slug>       worktreeを作る（.venv/.env はリンク共有）
  wt.sh diff   <repo> <slug>       本体との差分を見る
  wt.sh finish <repo> <slug>       本体にマージしてworktreeを片付ける
  wt.sh abort  <repo> <slug>       破棄する（確認あり）
  wt.sh list   [repo]              worktree一覧
  wt.sh clean  [repo]              壊れた登録を整理
USAGE
  exit 1 ;;
esac
