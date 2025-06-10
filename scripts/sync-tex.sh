#!/usr/bin/env bash
# sync-tex.sh ──────────────────────────────────────────────────
# Sync the entire classes/ tree (any files, any folders) from
# the site repo into the tex2html-api repo, then add/commit/push.
# --------------------------------------------------------------
set -euo pipefail

# ─── Paths (edit if your clones live elsewhere) ───────────────
SITE_CLASSES="$HOME/Documents/jerich/classes"
API_REPO="$HOME/Documents/tex2html-api"
API_CLASSES="$API_REPO/classes"

# ─── 1. Rsync everything that is new or newer -----------------
#  • -a      : archive (recursive, preserves perms, times, symlinks)
#  • --update: only copy if source newer or dest missing
#  • --delete-missing-dirs: prune dirs that vanished in source
#  • --delete-excluded     : keep the mirrors identical
#  • --exclude='.git/'     : skip any stray git dirs
# ─── 1. Rsync everything that is new or newer -----------------
rsync -a --update \
      --delete --prune-empty-dirs \
      --delete-excluded \
      --exclude='.git/' \
      "$SITE_CLASSES/"  "$API_CLASSES/"

# ─── 2. Commit & push in the API repo -------------------------
# --- 2. Commit & push in the API repo -------------------------
cd "$API_REPO"

git add -A classes

if git diff --cached --quiet; then
  echo "ℹ  No new files, folders, or .tex changes to sync."
  exit 0
fi

DATE=$(date +%F)
git commit -m "Sync classes/ from site repo – $DATE"

# NEW: make sure we're up-to-date before pushing
git pull --rebase --autostash  # fast if no one else pushed; auto-handles clashes
git push
echo "✔  Synced classes/ (including new files & folders) to tex2html-api."