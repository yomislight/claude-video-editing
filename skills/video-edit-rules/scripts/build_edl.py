"""Turn edl.txt (cue-based cut list) into frame-accurate source segments.

Cut points are estimated from the SRT (char-level by syllable interpolation),
then snapped to the nearest energy dip and padded toward the speech.
Long pauses inside kept pieces are shortened.
"""
import json, re, sys, wave
import numpy as np

FPS = 30
HOP = 0.01  # envelope resolution (s)

PAD_LINE = 0.06     # pad at a sentence (line) boundary -> ~0.12 s between sentences
PAD_JOIN = 0.04     # pad at a join inside a sentence
PAD_TIGHT = 0.02    # pad at a '+' join (word patched mid-phrase)
MAX_PAUSE = 0.20    # pauses longer than this inside a piece get shortened
KEEP_PAUSE = 0.10   # ...down to this

cues = {c['i']: c for c in json.load(open('cues.json', encoding='utf-8'))}

# ---------- envelope ----------
w = wave.open('audio16k.wav')
sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
hop = int(sr * HOP)
n = len(x) // hop
rms = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-10)
db = 20 * np.log10(rms)
# smooth a little (30 ms)
db_s = np.convolve(db, np.ones(3) / 3, mode='same')
floor = np.percentile(db_s, 8)
speech_lvl = np.percentile(db_s, 70)
THR = floor + 0.33 * (speech_lvl - floor)
print(f'floor {floor:.1f} dB, speech {speech_lvl:.1f} dB, thr {THR:.1f} dB', file=sys.stderr)

def fi(t):
    return int(min(max(t / HOP, 0), n - 1))

def loud(f):
    return db_s[f] > THR

# 'voiced' = clearly speech (ignores breaths / murmurs / tiny blips)
ON = floor + 0.5 * (speech_lvl - floor) + 3  # breath / murmur stays below this
from numpy.lib.stride_tricks import sliding_window_view
db_m = np.median(sliding_window_view(np.pad(db_s, 4, mode='edge'), 9), axis=1)  # 90 ms median: ignores clicks/blips

def voiced_run(f, step):
    return all(0 <= f + q * step < n and db_m[f + q * step] > ON for q in range(3))

def pause(f):
    return db_m[f] < ON

# ---------- char timing inside a cue ----------
def weights(text):
    out = []
    for tok in re.finditer(r'[A-Za-z]+|.', text):
        s = tok.group()
        if re.fullmatch(r'[A-Za-z]+', s):
            wgt = len(s) * (1.0 if (s.isupper() and len(s) <= 4) else 0.35)
            wgt = max(1.0, wgt) / len(s)
            out += [wgt] * len(s)
        elif s in ' ,，。、':
            out.append(0.0)
        else:
            out.append(1.0)
    return out

def speech_bounds(c):
    a, b = fi(c['s'] - 0.05), fi(c['e'] + 0.05)
    idx = [f for f in range(a, b + 1) if loud(f)]
    if not idx:
        return c['s'], c['e']
    return idx[0] * HOP, (idx[-1] + 1) * HOP

import os
CHARFIX = json.load(open('charfix.json')) if os.path.exists('charfix.json') else {}

HARD = json.load(open('hardcuts.json')) if os.path.exists('hardcuts.json') else {}

def char_time(ci, k):
    """time at boundary before char k of cue ci (k may equal len)."""
    if f'{ci}:{k}' in CHARFIX:
        return CHARFIX[f'{ci}:{k}']
    c = cues[ci]
    s, e = speech_bounds(c)
    wts = weights(c['text'])
    tot = sum(wts) or 1
    return s + (e - s) * sum(wts[:k]) / tot

# ---------- snapping ----------
def snap_in(est, win, pad):
    a, b = fi(est - win), fi(est + win)
    seg = db_s[a:b + 1]
    dist = np.abs(np.arange(a, b + 1) - est / HOP) * HOP
    m = a + int(np.argmin(seg + dist * 15))  # quietest, prefer close to estimate
    f = m
    while f < min(b + int(1.0 / HOP), n - 1) and not voiced_run(f, 1):
        f += 1
    onset = f * HOP
    return max(m * HOP, onset - pad)

def snap_out(est, win, pad):
    a, b = fi(est - win), fi(est + win)
    seg = db_s[a:b + 1]
    dist = np.abs(np.arange(a, b + 1) - est / HOP) * HOP
    m = a + int(np.argmin(seg + dist * 15))
    f = m
    while f > max(a - int(1.0 / HOP), 0) and not voiced_run(f - 1, -1):
        f -= 1
    offset = f * HOP
    return min(m * HOP, offset + pad)

# ---------- parse edl ----------
END_RE = r'(\d+)(?:\[(-?\d*):(-?\d*)\])?'

def parse_piece(tok):
    if tok.startswith('@'):
        # raw source range not covered by the SRT: @start-end=text
        span, _, text = tok[1:].partition('=')
        s, e = map(float, span.split('-'))
        cid = -(len([c for c in cues if c < 0]) + 1)
        cues[cid] = {'i': cid, 's': s, 'e': e, 'text': text}
        return cid, 0, cid, None
    if '-' in tok and not re.fullmatch(END_RE, tok):
        # range: A-B   (A may carry [a:], B may carry [:b])
        m = re.fullmatch(END_RE + '-' + END_RE, tok)
        i, a, _, j, _, b = m.groups()
        return int(i), (int(a) if a else 0), int(j), (int(b) if b else None)
    m = re.fullmatch(END_RE, tok)
    i, a, b = m.groups()
    i = int(i)
    return i, (int(a) if a else 0), i, (int(b) if b else None)

lines = []
for raw in open('edl.txt', encoding='utf-8'):
    raw = raw.split('#')[0].strip()
    if not raw:
        continue
    pieces, joins = [], []
    for k, grp in enumerate(raw.split(' ')):
        for m, tok in enumerate(grp.split('+')):
            if pieces:
                joins.append('tight' if m > 0 else 'join')
            pieces.append(parse_piece(tok))
    lines.append((raw, pieces, joins))

def norm_idx(text, k):
    if k is None:
        return len(text)
    return k if k >= 0 else len(text) + k

segments, report = [], []
for li, (raw, pieces, joins) in enumerate(lines):
    for pi, (i, a, j, b) in enumerate(pieces):
        ti, tj = cues[i]['text'], cues[j]['text']
        a = norm_idx(ti, a)
        b = norm_idx(tj, b)
        pad_in = PAD_LINE if pi == 0 else (PAD_TIGHT if joins[pi - 1] == 'tight' else PAD_JOIN)
        pad_out = PAD_LINE if pi == len(pieces) - 1 else (PAD_TIGHT if joins[pi] == 'tight' else PAD_JOIN)
        if f'{i}:{a}' in HARD:
            t_in = HARD[f'{i}:{a}']
        elif a == 0:
            t_in = snap_in(speech_bounds(cues[i])[0], 0.25, pad_in)
        else:
            t_in = snap_in(char_time(i, a), 0.22, pad_in)
        if f'{j}:{b}' in HARD:
            t_out = HARD[f'{j}:{b}']
        elif b == len(tj):
            t_out = snap_out(speech_bounds(cues[j])[1], 0.25, pad_out)
        else:
            t_out = snap_out(char_time(j, b), 0.22, pad_out)
        if i == j:
            text = ti[a:b]
        else:
            text = ti[a:] + ''.join(cues[c]['text'] for c in range(i + 1, j)) + tj[:b]
        # shorten long internal pauses
        parts, cur = [], t_in
        f, fend = fi(t_in + 0.05), fi(t_out - 0.05)
        while f < fend:
            if pause(f):
                g = f
                while g < fend and pause(g):
                    g += 1
                if (g - f) * HOP > MAX_PAUSE:
                    half = KEEP_PAUSE / 2
                    parts.append((cur, f * HOP + half))
                    cur = g * HOP - half
                f = g
            f += 1
        parts.append((cur, t_out))
        # drop fragments that hold no actual speech (silence / murmur left by a cut point)
        parts = [p for p in parts if any(all(db_s[g + q] > ON + 8 for q in range(3)) for g in range(fi(p[0]), fi(p[1]) - 2))] or parts
        for p in parts:
            segments.append({'line': li, 'in': p[0], 'out': p[1]})
        subs = []
        for c in range(i, j + 1):
            tc = cues[c]['text']
            ca = a if c == i else 0
            cb = b if c == j else len(tc)
            s0 = t_in if c == i else speech_bounds(cues[c])[0]
            e0 = t_out if c == j else speech_bounds(cues[c])[1]
            if tc[ca:cb].strip():
                subs.append((max(s0, t_in), min(e0, t_out), tc[ca:cb]))
        report.append({'line': li, 'edl': raw, 'piece': pi, 'text': text, 'in': t_in, 'out': t_out, 'subs': subs,
                       'pauses_cut': len(parts) - 1})

# frame quantize + merge contiguous
q = []
for s in segments:
    fin, fout = round(s['in'] * FPS), round(s['out'] * FPS)
    if fout - fin < 2:
        fout = fin + 2
    if q and fin <= q[-1][1] + 1 and fin >= q[-1][0]:
        q[-1][1] = max(q[-1][1], fout)
        continue
    q.append([fin, fout, s['line']])

json.dump({'fps': FPS, 'segments': q}, open('segments.json', 'w'))
json.dump(report, open('report.json', 'w'), ensure_ascii=False, indent=1)
tot = sum(b - a for a, b, _ in q) / FPS
print(f'{len(q)} segments, total {tot/60:.2f} min ({tot:.1f}s)', file=sys.stderr)
