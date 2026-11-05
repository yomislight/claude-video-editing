"""Render the rough cut: frame-exact per-segment video encodes -> concat (copy) -> mux with cut_audio.wav."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

SRC = os.path.abspath(os.environ.get('SRC', '../source.mp4'))
OUT = os.path.abspath(os.environ.get('OUT', '../rough_cut.mp4'))
d = json.load(open('segments.json'))
fps, segs = d['fps'], d['segments']
os.makedirs('segs', exist_ok=True)
for f in os.listdir('segs'):
    os.remove(os.path.join('segs', f))

def enc(k):
    a, b, _ = segs[k]
    path = f'segs/s{k:04d}.mp4'
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-hwaccel', 'videotoolbox',
           '-ss', f'{a / fps - 0.008:.4f}', '-i', SRC, '-frames:v', str(b - a), '-an',
           '-vf', f'fps={fps}', '-c:v', 'h264_videotoolbox', '-b:v', '16M', '-profile:v', 'high',
           '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360', path]
    subprocess.run(cmd, check=True)
    return k

with ThreadPoolExecutor(4) as ex:
    for n, k in enumerate(ex.map(enc, range(len(segs)))):
        if n % 20 == 0:
            print(f'{n}/{len(segs)}', flush=True)

with open('segs/list.txt', 'w') as f:
    for k in range(len(segs)):
        f.write(f"file 's{k:04d}.mp4'\n")
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0',
                '-i', 'segs/list.txt', '-i', 'cut_audio.wav', '-map', '0:v', '-map', '1:a',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', OUT], check=True)
print('done', OUT)
