#!/usr/bin/env python3
"""檢查詳情頁裡的 YouTube 章節能不能被識別。
usage: python3 check_chapters.py 詳情頁.txt [影片秒數]
規則：每個時間點單獨一行且在行首；第一個是 0:00；遞增；至少 3 章；每章 ≥ 10 秒；不超過片長。
"""
import re, sys
txt = open(sys.argv[1], encoding='utf-8').read()
dur = float(sys.argv[2]) if len(sys.argv) > 2 else None
pat = re.compile(r'^(?:(\d+):)?(\d{1,2}):(\d{2})\s+(\S.*)$')
ch, bad = [], []
for n, line in enumerate(txt.splitlines(), 1):
    m = pat.match(line.strip())
    if m:
        h, mm, ss, title = m.groups()
        ch.append((int(h or 0) * 3600 + int(mm) * 60 + int(ss), title, n))
    elif re.search(r'\d{1,2}:\d{2}\s+\S+.*\d{1,2}:\d{2}\s', line):
        bad.append(f'第 {n} 行有多個時間點擠在同一行（換行丟了）')
err = list(bad)
if len(ch) < 3: err.append(f'只找到 {len(ch)} 個章節，至少要 3 個')
if ch and ch[0][0] != 0: err.append('第一個章節必須是 0:00')
for (a, ta, na), (b, tb, nb) in zip(ch, ch[1:]):
    if b <= a: err.append(f'第 {nb} 行時間沒有遞增')
    elif b - a < 10: err.append(f'「{ta}」只有 {b - a} 秒，每章至少 10 秒')
if dur and ch:
    if ch[-1][0] >= dur: err.append('最後一章超過片長')
    elif dur - ch[-1][0] < 10: err.append('最後一章不到 10 秒')
for t, title, n in ch:
    print(f'{t // 60}:{t % 60:02d}  {title}')
print('\n' + ('\n'.join('✗ ' + e for e in err) if err else f'✓ {len(ch)} 個章節，格式正確'))
sys.exit(1 if err else 0)
