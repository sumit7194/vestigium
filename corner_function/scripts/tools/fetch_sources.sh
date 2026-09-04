#!/bin/sh
# Re-create the source-text working set used by report.md / RESULT.md.
#
# The paper texts themselves are NOT stored in this repo (third-party content,
# ~4 MB, all publicly re-fetchable). This script regenerates them byte-for-byte
# with the same converter, which is what makes the ar5iv line numbers quoted in
# RESULT.md Sec. 9 reproducible.
#
# Usage:  sh scripts/tools/fetch_sources.sh [outdir]     (default: ./sources)
set -e
OUT=${1:-sources}
mkdir -p "$OUT"

# key | arXiv id | host
#   ar5iv  = https://ar5iv.labs.arxiv.org/html/<id>   (older papers)
#   native = https://arxiv.org/html/<id>              (LaTeXML-native, 2024+)
set -- \
  "BWK16    1511.04077     ar5iv" \
  "CCT09    0905.2069      ar5iv" \
  "BMW15b   1507.06997     ar5iv" \
  "CH09     0905.2562      ar5iv" \
  "HMSY11   1110.1084      ar5iv" \
  "Sac93    hep-th/9305131 ar5iv" \
  "PSN99    hep-th/9812166 ar5iv" \
  "AM26     2608.23692     native"

for row in "$@"; do
  key=$(echo "$row" | awk '{print $1}')
  id=$(echo  "$row" | awk '{print $2}')
  host=$(echo "$row" | awk '{print $3}')
  file=$(echo "$id" | tr '/' '_')
  if [ "$host" = "native" ]; then url="https://arxiv.org/html/$id"
  else url="https://ar5iv.labs.arxiv.org/html/$id"; fi
  echo "[$key] $url"
  curl -sL --max-time 90 -o "$OUT/$file.html" "$url"
  python3 "$(dirname "$0")/h2t.py" "$OUT/$file.html" >/dev/null
done

echo
echo "Done. Grep with context:  python3 scripts/tools/ctx.py $OUT/<file>.txt '<regex>' 2"
echo "Note: the CH09 (0905.2562) conversion drops the kappa_d table; see TODO.md."
