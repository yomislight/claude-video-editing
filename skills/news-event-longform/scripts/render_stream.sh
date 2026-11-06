#!/bin/zsh
# 長片渲染：--workers 1 讓畫面直接串流進編碼器，不在硬碟落幀。
# 多 worker 會先把全部幀寫到暫存（16 分鐘 1080p 約 28GB）；--start/--end 分段會撞 2GB 的 PLAN_TOO_LARGE。
# usage: render_stream.sh <hyperframes 工程目錄> <輸出 mp4>
set -e
PROJ=$1; OUT=$2
HF=${HF:-hyperframes}
CACHE="$(getconf DARWIN_USER_TEMP_DIR)hyperframes-extract-cache-$(id -u)"
echo "free: $(df -h "$PROJ" | tail -1 | awk '{print $4}')  extract cache: $(du -sh "$CACHE" 2>/dev/null | cut -f1)"
cd "$PROJ"
$HF check . || true            # text_occluded 來自背景字元雨可忽略，其他錯誤要先修
$HF render . --workers 1 -o "$OUT"
echo "RENDER_EXIT=$?"
# 渲染完的質檢
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact "$OUT"
ffmpeg -hide_banner -nostats -i "$OUT" -af volumedetect -vn -f null - 2>&1 | grep -E 'mean_volume|max_volume'
ffmpeg -hide_banner -nostats -i "$OUT" -af silencedetect=n=-45dB:d=3 -vn -f null - 2>&1 | grep -c silence_start | xargs echo "silences>3s:"
