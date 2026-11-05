"""Render the rough cut from segments.json.

audio: sample-accurate splice of audio48k.wav with short fades at every cut
video: one-pass ffmpeg select over the source (frame-aligned segments)
then mux.  Usage: python render.py [--audio-only]
"""
import os, json, subprocess, sys, wave
import numpy as np

SRC = os.environ.get('SRC', '../source.mp4')  # 去过水印或图标的原片
d = json.load(open('segments.json'))
fps, segs = d['fps'], d['segments']
SR = 48000
FADE = int(0.008 * SR)

w = wave.open('audio48k.wav')
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(np.float32)
out = []
ramp = np.linspace(0, 1, FADE, dtype=np.float32)[:, None]
for fin, fout, _ in segs:
    s, e = fin * SR // fps, fout * SR // fps
    chunk = a[s:e].copy()
    chunk[:FADE] *= ramp
    chunk[-FADE:] *= ramp[::-1]
    out.append(chunk)
audio = np.concatenate(out)
wo = wave.open('cut_audio.wav', 'wb')
wo.setnchannels(2); wo.setsampwidth(2); wo.setframerate(SR)
wo.writeframes(np.clip(audio, -32768, 32767).astype(np.int16).tobytes())
wo.close()
print(f'audio {len(audio)/SR:.2f}s', file=sys.stderr)
if '--audio-only' in sys.argv:
    sys.exit()

# video select expression on frame numbers
expr = '+'.join(f'between(t,{(fin-0.5)/fps:.4f},{(fout-0.5)/fps:.4f})' for fin, fout, _ in segs)
cmd = ['ffmpeg', '-hide_banner', '-y', '-hwaccel', 'videotoolbox', '-i', SRC, '-i', 'cut_audio.wav',
       '-filter_complex_script', 'vf.txt', '-map', '[v]', '-map', '1:a',
       '-c:v', 'h264_videotoolbox', '-b:v', '16M', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
       '-r', str(fps), '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart',
       os.environ.get('OUT', '../rough_cut.mp4')]
open('vf.txt', 'w').write(f"[0:v]select='{expr}',setpts=N/{fps}/TB,fps={fps}[v]")
subprocess.run(cmd, check=True)
