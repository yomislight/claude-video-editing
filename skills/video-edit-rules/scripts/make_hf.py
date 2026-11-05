"""Write hf_studio/index.html: the rough cut as a HyperFrames timeline (for watching in Studio).
Track 0 = the cut clips (720p proxy), track 1 = which script line is playing."""
import json, html

d = json.load(open('segments.json'))
fps, segs = d['fps'], d['segments']
rep = json.load(open('report.json', encoding='utf-8'))
line_text = {}
FIX=[('Cloud Code','Claude Code'),('Cloud','Claude'),('cloud','Claude'),('premium','Premiere'),('FM Page','FFmpeg'),('剪印','剪映'),('黑镜','HeyGen'),('幽密','yomi'),('桌面板','桌面版'),('资料源','资料员'),('Hyperframes','HyperFrames'),('Hello','哈喽'),('Paracate','Parakeet'),('epidemic','Epidemic'),('减硬','剪辑'),('寄到','记到'),('open screen','Openscreen'),('OpenScreen','Openscreen'),('whisper','Whisper'),('每减一支','每剪一支'),('一只','一支'),('整只','整支'),('这条系统','这套系统')]
for r in rep:
    for a,b in FIX:
        r['text']=r['text'].replace(a,b)
for r in rep:
    line_text[r['line']] = line_text.get(r['line'], '') + ('｜' if r['line'] in line_text else '') + r['text']

clips, labels, off = [], [], 0
line_span = {}
for k, (a, b, l) in enumerate(segs):
    st, du, ms = off / fps, (b - a) / fps, a / fps
    clips.append(f'      <video id="c{k+1}" class="clip cut" src="assets/proxy.mp4" playsinline muted '
                 f'data-start="{st:.4f}" data-duration="{du:.4f}" data-media-start="{ms:.4f}" data-track-index="0"></video>')
    s0, e0 = line_span.get(l, (st, st + du))
    line_span[l] = (min(s0, st), st + du)
    off += b - a
total = off / fps
for l, (s, e) in sorted(line_span.items()):
    labels.append(f'      <div id="l{l+1}" class="clip label" data-start="{s:.4f}" data-duration="{e-s:.4f}" data-track-index="1">'
                  f'<span>#{l+1}　{html.escape(line_text.get(l, ""))}</span></div>')

import os
AUDIO = open('audio_name.txt').read().strip() if os.path.exists('audio_name.txt') else 'cut_audio.m4a'
page = f'''<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>粗剪</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      body {{ margin: 0; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }}
      .cut {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .label {{ position: absolute; left: 40px; right: 40px; top: 32px; display: flex; }}
      .label span {{ background: rgba(0,0,0,.62); color: #fff; font: 600 30px/1.35 system-ui, sans-serif;
                     padding: 10px 18px; border-radius: 8px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="{total:.4f}">
{chr(10).join(clips)}
{chr(10).join(labels)}
      <audio id="cutaudio" src="assets/{AUDIO}" data-start="0" data-duration="{total:.4f}" data-track-index="2" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''
open('../hf_studio/index.html', 'w', encoding='utf-8').write(page)
print(len(segs), 'clips', len(labels), 'labels', f'{total:.1f}s')
