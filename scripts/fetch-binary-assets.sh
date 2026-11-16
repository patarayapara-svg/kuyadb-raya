#!/usr/bin/env bash
# Restores the binary files (images, fonts, PDFs) listed in scripts/binary-assets.sha256
# by downloading them from the live site and checking each SHA-256.
# Then mirrors them into assets/ so `python3 src/build.py` can rebuild public/.
# Usage: bash scripts/fetch-binary-assets.sh [base-url]
set -euo pipefail
cd "$(dirname "$0")/.."
BASE="${1:-https://pataraya-pilot.vercel.app}"
fail=0
while read -r sum size path; do
  [[ -z "${sum:-}" || "$sum" == \#* ]] && continue
  url="$BASE/${path#public/}"
  mkdir -p "$(dirname "$path")"
  if [[ -f "$path" ]] && echo "$sum  $path" | sha256sum -c --status; then continue; fi
  curl -fsSL "$url" -o "$path.tmp"
  if echo "$sum  $path.tmp" | sha256sum -c --status; then mv "$path.tmp" "$path"; echo "ok   $path";
  else echo "BAD  $path (checksum mismatch)"; rm -f "$path.tmp"; fail=1; fi
done < scripts/binary-assets.sha256
# mirror into assets/ (source folder used by src/build.py)
mkdir -p assets/img assets/fonts assets/vendor assets/downloads
cp -f public/assets/img/* assets/img/
find public/assets/fonts -name '*.woff2' -exec cp -f {} assets/fonts/ \;
cp -f public/assets/og.jpg assets/og.jpg
cp -f public/assets/vendor/supabase.js assets/vendor/supabase.js
cp -f public/downloads/* assets/downloads/ 2>/dev/null || true
exit $fail
