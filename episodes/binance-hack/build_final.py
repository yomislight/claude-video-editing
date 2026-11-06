"""Generate hf_final/index.html: the finished episode as one HyperFrames composition.

Timeline:  teaser1 | teaser2 | hook (cut 0 → line 9) | Crypto Future sting | body | thank-you card
A-roll picture = beauty version (same frames as the locked cut), sound = original cut audio.
"""
import json, html, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

FPS = 30
OUT = '../hf_final/index.html'
segs = json.load(open('segments.json'))['segments']
rep = json.load(open('report.json', encoding='utf-8'))
CUT_LEN = sum(b - a for a, b, _ in segs) / FPS

# ---------- line timing in locked-cut time ----------
seg_off, o = [], 0
for a, b, l in segs:
    seg_off.append((a / FPS, b / FPS, o / FPS, l)); o += b - a
line_ids = sorted({l for *_, l in seg_off})
LS, LE = {}, {}
for n, l in enumerate(line_ids, 1):
    ss = [z for z in seg_off if z[3] == l]
    LS[n] = ss[0][2]; LE[n] = ss[-1][2] + (ss[-1][1] - ss[-1][0])
NLINES = len(line_ids)

def src_to_cut(t, side):
    """map an original-footage time to locked-cut time; side='in' snaps forward, 'out' back."""
    best = None
    for a, b, off, l in seg_off:
        if a - 1e-3 <= t <= b + 1e-3:
            return off + min(max(t, a), b) - a
        if side == 'in' and t < a and (best is None or a < best[0]):
            best = (a, off)
        if side == 'out' and t > b and (best is None or b > best[0]):
            best = (b, off + (b - a))
    return best[1] if best else 0.0

# ---------- final timeline ----------
P1 = (LS[109], LE[110]); P2 = (LS[69], LE[69])
D1, D2 = P1[1] - P1[0], P2[1] - P2[0]
TEASE = D1 + D2
STING = 4.0
SPLIT = LS[9]                       # sting goes right after "就一起看下去吧"
END_CARD = 5.966
TOTAL = TEASE + CUT_LEN + STING + END_CARD

def T(t):
    """locked-cut time -> final time"""
    return TEASE + t + (STING if t >= SPLIT - 1e-6 else 0)

BODY_END = T(CUT_LEN)

# ---------- subtitles ----------
FIX = [('优米老师', 'YOMI 老师'), ('优蜜', 'YOMI'), ('BYBIT', 'Bybit'), ('币币的', 'Bybit 的'),
       ('financeforty', 'Binance 14'), ('finance fourteen', 'Binance 14'), ('Binance Fourteen', 'Binance 14'),
       ('Binance fourteen', 'Binance 14'), ('binance fourteen', 'Binance 14'), ('binancefourteen', 'Binance 14'),
       ('binanceforte', 'Binance 14'), ('pants', 'pyenv'), ('Patra', 'Pectra'), ('blockcha i n', 'Blockaid'),
       ('Bloqcha i n', 'Blockaid'), ('blog egg', 'Blockaid'), ('Trader Trader', 'TraderTraitor'),
       ('23,346亿枚', '2.3346 亿枚'), ('noncenumber used once', 'nonce（number used once）'),
       ('EIP7702', 'EIP-7702'), ('EIP 7702', 'EIP-7702'), ('q day', 'Q-Day'), ('TOKEN', 'Token'),
       ('AI agent', 'AI Agent'), ('转加', '转嫁'), ('盗劫', '盗窃'), ('爬取', '扒取'), ('BN在', '币安在'),
       ('optioptimism', 'Optimism'), ('optimism', 'Optimism'), ('索拉纳', 'Solana')]

def clean(t):
    for a, b in FIX:
        t = t.replace(a, b)
    t = re.sub(r'[啊呀]$', '', t)
    return t.strip()

subs = []
for r in rep:
    for s, e, txt in r['subs']:
        a, b = src_to_cut(s, 'in'), src_to_cut(e, 'out')
        if b - a < 0.25:
            continue
        txt = clean(txt)
        if not txt:
            continue
        if len(txt) > 17:          # split long lines in two, timed by length
            k = len(txt) // 2
            m = a + (b - a) * k / len(txt)
            subs += [(a, m, txt[:k]), (m, b, txt[k:])]
        else:
            subs.append((a, b, txt))
subs.sort()
# no overlaps
for i in range(len(subs) - 1):
    if subs[i][1] > subs[i + 1][0]:
        subs[i] = (subs[i][0], subs[i + 1][0], subs[i][2])

def sub_final():
    out = []
    for a, b, t in subs:        # teaser copies
        for (p0, p1), base in ((P1, 0), (P2, D1)):
            if a >= p0 - 0.05 and b <= p1 + 0.05:
                out.append((base + a - p0, base + min(b, p1) - p0, t))
    for a, b, t in subs:
        out.append((T(a), T(b), t))
    return out

# ---------- B-roll ----------
import broll2 as broll
from broll2 import jz

# ---------- assemble ----------
clips, css_extra, js = [], [], []
def clip(html_, start, dur, track, cls='', idattr=''):
    clips.append(html_.format(start=f'{start:.3f}', dur=f'{max(dur, 0.04):.3f}', track=track))

def aroll(id_, start, dur, mstart):
    clips.append(f'<video id="{id_}" class="clip aroll" src="assets/aroll.mp4" muted playsinline '
                 f'data-start="{start:.3f}" data-duration="{dur:.3f}" data-media-start="{mstart:.3f}" data-track-index="0"></video>')

def voice(id_, start, dur, mstart):
    clips.append(f'<audio id="{id_}" src="assets/voice.m4a" data-start="{start:.3f}" data-duration="{dur:.3f}" '
                 f'data-media-start="{mstart:.3f}" data-track-index="30" data-volume="1"></audio>')

# A-roll picture + voice
cam_clips = []
for id_, st, du, ms in (('t1', 0, D1, P1[0]), ('t2', D1, D2, P2[0]),
                        ('m1', TEASE, SPLIT, 0), ('m2', TEASE + SPLIT + STING, CUT_LEN - SPLIT, SPLIT)):
    # teaser framing set by hand in Studio
    st_attr = {'t1': ' style="translate:74.194px 0.078px;width:1764px;height:992px"',
               't2': ' style="translate:85.353px 5.978px;width:1742px;height:980px"'}.get(id_, '')
    cam_clips.append(f'<video id="{id_}"{st_attr} class="clip aroll" src="assets/aroll.mp4" muted playsinline '
                     f'data-start="{st:.3f}" data-duration="{du:.3f}" data-media-start="{ms:.3f}" data-track-index="0"></video>')
    voice('v' + id_, st, du, ms)

# sting + end card
clips.append(f'<video id="sting" class="clip full" src="assets/sting.mp4" muted playsinline data-start="{TEASE + SPLIT:.3f}" '
             f'data-duration="{STING:.3f}" data-track-index="1"></video>')
clips.append(f'<video id="endcard" class="clip full" src="assets/endcard.mp4" muted playsinline data-start="{BODY_END:.3f}" '
             f'data-duration="{END_CARD:.3f}" data-track-index="1"></video>')

# teaser labels + white flashes
for n, t in enumerate((D1, TEASE), 1):
    clips.append(f'<div id="flash{n}" class="clip flash" data-start="{t - 0.12:.3f}" data-duration="0.36" data-track-index="13"><div class="flashin"></div></div>')
    js.append(f'tl.fromTo("#flash{n} .flashin", {{opacity: 0}}, {{opacity: 1, duration: 0.12, ease: "none"}}, {t - 0.12:.3f});'
              f'tl.to("#flash{n} .flashin", {{opacity: 0, duration: 0.24, ease: "power2.out"}}, {t:.3f});')

# logo (off during teasers' label? keep on; off during sting and end card)
for n, (st, en) in enumerate(((0, TEASE + SPLIT), (TEASE + SPLIT + STING, BODY_END)), 1):
    clips.append(f'<img id="logo{n}" class="clip logo" src="assets/logo.png" data-start="{st:.3f}" data-duration="{en - st:.3f}" data-track-index="14">')

ACC = ['Binance 14','EIP-7702','TraderTraitor','Homebrew','Blockaid','Elliptic','Optimism','Solana','pyenv','Bybit','nonce','Token','Q-Day','YOMI','币安','FBI','XRP','BTC','ETH','USDT','USDC','黑客','私钥','签名服务','授权','冻结']
NUM = r'[$]?\d[\d,.]*\s*(?:亿|万|枚|秒|分钟|分|个月|月|日|号|%|倍)?'
accrx = re.compile(NUM + '|' + '|'.join(map(re.escape, sorted(ACC, key=len, reverse=True))))
clips.append(f'<div id="scrim" class="clip scrim" data-start="0" data-duration="{BODY_END:.3f}" data-track-index="19"></div>')
for k, (a, b, t) in enumerate(sub_final()):
    t2 = accrx.sub(lambda m: f'\x01{m.group(0)}\x02', t, count=1)
    t2 = jz(html.escape(t2)).replace('\x01', '<b>').replace('\x02', '</b>')
    clips.append(f'<div id="s{k}" class="clip cap" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="20">'
                 f'<span>{t2}</span></div>')

# keyword timing inside a line ("說到什麼就出什麼")
by_line = {}
for r in rep:
    by_line.setdefault(r['line'], []).extend(r['subs'])
missing = []
def word_time(n, kw):
    for s0, e0, txt in by_line[line_ids[n - 1]]:
        i = txt.lower().find(kw.lower())
        if i >= 0:
            src = s0 + (e0 - s0) * i / max(len(txt), 1)
            return T(src_to_cut(src, 'in'))
    missing.append((n, kw)); return T(LS[n])

extra_audio, overrides, under = [], [], []
if broll:
    b = broll.build(dict(T=T, LS=LS, LE=LE, TEASE=TEASE, SPLIT=SPLIT, STING=STING, BODY_END=BODY_END, TOTAL=TOTAL,
                         D1=D1, D2=D2, P1=P1, P2=P2, word_time=word_time))
    under = b.get('under', []); clips += b['clips']; css_extra.append(b.get('css', '')); js.append(b.get('js', ''))
    extra_audio += b.get('audio', []); overrides = b.get('cam', [])
if missing:
    print('keywords not found:', missing)

pushes = b.get('push', []) if broll else []
for st, en, sd in overrides:
    dx = 120 if sd == 'L' else -120
    js.append(f'tl.fromTo("#cam",{{x:0,scale:1}},{{x:{dx},scale:1.14,duration:.5,ease:"power3.inOut",immediateRender:false}},{st:.3f});')
    js.append(f'tl.fromTo("#cam",{{x:{dx},scale:1.14}},{{x:0,scale:1,duration:.32,ease:"power2.inOut",immediateRender:false}},{en - .32:.3f});')
for st, en, a_, b_ in pushes:
    if any(o[0] < en and st < o[1] for o in overrides):
        continue
    js.append(f'tl.fromTo("#cam",{{scale:{a_}}},{{scale:{b_},duration:{en - st:.2f},ease:"none",immediateRender:false}},{st:.3f});tl.set("#cam",{{scale:1}},{en:.3f});')

clips += extra_audio

page = f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>幣安被盜 63 億｜成片</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
body {{ margin: 0; background: #07090f; }}
#root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #07090f; }}
#cam {{ position: absolute; inset: 0; transform-origin: 50% 47%; }}
.aroll {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.full {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.logo {{ position: absolute; top: -83.271px; right: 0.521px; width: 400px; height: 400px; z-index: 15; }}  /* user-set in Studio, one position for the whole film */
.flash {{ position: absolute; inset: 0; z-index: 30; }}
.flashin {{ position: absolute; inset: 0; background: #fff; opacity: 0; }}
.cap {{ position: absolute; left: 0; right: 0; bottom: 60px; text-align: center; z-index: 20; }}
.cap span {{ display: inline-block; font: 400 56px/1.25 "Jiezou"; letter-spacing: 2px; color: #fff; text-shadow: 0 2px 3px rgba(0,0,0,.55), 0 4px 22px rgba(0,0,0,.6); }}
.cap b {{ color: #3CFFA0; font-weight: 400; }} .cap u {{ font-size: 56px; }}
{''.join(css_extra)}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="{TOTAL:.3f}">
{chr(10).join(under)}
<div id="cam">
{chr(10).join(cam_clips)}
</div>
{chr(10).join(clips)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
open(OUT, 'w', encoding='utf-8').write(page)
print(f'total {TOTAL:.2f}s  teaser {TEASE:.2f}s  body ends {BODY_END:.2f}s  subs {len(subs)}  clips {len(clips)}')
