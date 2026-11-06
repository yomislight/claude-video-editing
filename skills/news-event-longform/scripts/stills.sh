#!/bin/zsh
# 從美顏版 A-roll 抽人物圖給封面用：每個時間點一張原尺寸 PNG + 一張 2x2 預覽拼圖。
# usage: stills.sh <影片> <輸出目錄> <前綴> t1 t2 t3 t4
# 選圖原則：半身、帶手勢、微笑有親和感；眼睛睜開、嘴型自然。
set -e
SRC=$1; OUT=$2; P=$3; shift 3; mkdir -p "$OUT"
i=0; ins=()
for t in "$@"; do i=$((i+1)); f="$OUT/${P}_0$i.png"
  ffmpeg -hide_banner -loglevel error -y -ss $t -i "$SRC" -frames:v 1 "$f"; ins+=(-i "$f"); done
if [ $i -eq 4 ]; then
  ffmpeg -hide_banner -loglevel error -y "${ins[@]}" -filter_complex \
   "[0]scale=640:-1[a];[1]scale=640:-1[b];[2]scale=640:-1[c];[3]scale=640:-1[d];[a][b]hstack[t];[c][d]hstack[u];[t][u]vstack" "$OUT/${P}_預覽.jpg"
fi
ls "$OUT"
