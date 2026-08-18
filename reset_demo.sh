#!/usr/bin/env bash
# reset_demo.sh -- restore demo-inbox/ to its pristine messy starting state.
# Safe to run before every rehearsal or every live take: it deletes whatever
# demo-inbox/ currently looks like (organized subfolders, undo log, all of
# it) and copies a fresh, untouched copy from fixtures-pristine/.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d fixtures-pristine ]; then
  echo "fixtures-pristine/ is missing -- run: python3 scripts/generate_fixtures.py"
  exit 1
fi

rm -rf demo-inbox
mkdir demo-inbox
cp fixtures-pristine/* demo-inbox/
echo "demo-inbox/ reset to $(ls demo-inbox | wc -l | tr -d ' ') pristine file(s)."
