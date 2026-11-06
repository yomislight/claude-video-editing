#!/bin/zsh
# 把 yt_rec.mjs 錄到的 webm 轉成好 seek 的 mp4（-g 15，靜音），原檔移到 RAW 目錄。
# usage: yt_transcode.sh <assets/yt 目錄> <原檔備份目錄>
set -e
DIR=$1; RAW=$2; mkdir -p "$RAW"; cd "$DIR"
for f in *.webm(N); do
  ffmpeg -hide_banner -loglevel error -y -i "$f" -an -r 30 -c:v libx264 -crf 20 -preset veryfast -g 15 \
    -pix_fmt yuv420p -movflags +faststart "${f%.webm}.mp4"
  mv "$f" "$RAW/"
done
ls -la *.mp4
