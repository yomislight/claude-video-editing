"""B-roll v2 — the Claude-tutorial look (dark aurora scenes, glass cards, one teal accent, Jiezou type,
Mixkit SFX), applied to the Binance episode. Keeps the 加密未來 logo / teasers / sting / end card.
build(ctx) -> {'clips','css','js','audio','cam','push'}
"""
import json, html, re, math

SH = json.load(open('../hf_final/assets/shots/shots.json'))
E = html.escape
A = '#3CFFA0'      # the one accent (hacker green)
R = '#ff6b6b'      # danger, used sparingly

# ---------- Jiezou: feed Simplified, it draws Traditional; patch one-to-many chars with MiSans ----------
PATCH = {'后': '後', '干': '幹', '松': '鬆', '准': '準', '线': '線', '复杂': '複雜', '里程': '里程'}
def jz(s):
    s = s.replace('后台', '后<u>台</u>').replace('复杂', '<u>複</u>杂')
    return re.sub('[后干松准线]', lambda m: f'<u>{PATCH[m.group(0)]}</u>', s)

# ---------- line icons (own simple paths, stroke-based) ----------
ICON = {
 'hacker': '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/><path d="M8 8h8"/>',
 'tool': '<path d="M14.5 5.5a4 4 0 00-5 5L4 16v4h4l5.5-5.5a4 4 0 005-5l-2.5 2.5-2.5-.5-.5-2.5z"/>',
 'brief': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V4h6v3M3 12h18"/>',
 'cpu': '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
 'key': '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3M15 8l2 2"/>',
 'lock': '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/>',
 'wallet': '<rect x="3" y="6" width="18" height="14" rx="2.5"/><path d="M3 10h18M16 15h2"/>',
 'coins': '<ellipse cx="9" cy="7" rx="6" ry="3"/><path d="M3 7v5c0 1.7 2.7 3 6 3s6-1.3 6-3V7"/><path d="M9 15v2c0 1.7 2.7 3 6 3s6-1.3 6-3v-5c0-1.7-2.7-3-6-3"/>',
 'file': '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
 'shield': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
 'server': '<rect x="4" y="4" width="16" height="7" rx="1.5"/><rect x="4" y="13" width="16" height="7" rx="1.5"/><path d="M8 7.5h.01M8 16.5h.01"/>',
 'laptop': '<rect x="5" y="5" width="14" height="10" rx="1.5"/><path d="M2 19h20"/>',
 'alert': '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
 'pkg': '<path d="M12 3l9 5v8l-9 5-9-5V8z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
 'chain': '<rect x="2" y="9" width="9" height="6" rx="3"/><rect x="13" y="9" width="9" height="6" rx="3"/><path d="M9 12h6"/>',
 'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 'snow': '<path d="M12 2v20M4 6l16 12M20 6L4 18"/>',
 'fire': '<path d="M12 3c1 4 5 5 5 10a5 5 0 01-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3-1-6 1-9z"/>',
 'puzzle': '<path d="M4 8h4a2 2 0 114 0h4v4a2 2 0 110 4v4H4v-4a2 2 0 100-4z"/>',
 'check': '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
 'x': '<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>',
 'users': '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.5 3-6 6.5-6s6.5 2.5 6.5 6"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14c3 0 5.5 2 5.5 5"/>',
 'code': '<path d="M8 8l-5 4 5 4M16 8l5 4-5 4M14 5l-4 14"/>',
 'pen': '<path d="M15 4l5 5L9 20H4v-5z"/><path d="M13 6l5 5"/>',
 'pause': '<circle cx="12" cy="12" r="9"/><path d="M10 9v6M14 9v6"/>',
 'atom': '<circle cx="12" cy="12" r="1.5"/><ellipse cx="12" cy="12" rx="9" ry="3.5"/><ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(120 12 12)"/>',
 'search': '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
 'chat': '<path d="M4 5h16v11H9l-5 4V5z"/>',
 'stamp': '<path d="M9 3h6v6l-1 3h4v4H6v-4h4l-1-3z"/><path d="M5 20h14"/>',
 'bolt': '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
 'gas': '<path d="M5 21V5a2 2 0 012-2h6a2 2 0 012 2v16M3 21h14M15 9h2a2 2 0 012 2v6a1.5 1.5 0 003 0V8l-3-3"/>',
 'eye': '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 'bell': '<path d="M6 16V11a6 6 0 1112 0v5l2 2H4l2-2zM10 21h4"/>',
 'bank': '<path d="M3 10l9-6 9 6M5 10v8M9 10v8M15 10v8M19 10v8M3 21h18"/>',
}
def svg(k, cls=''):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICON[k]}</svg>'

CSS = f'''
@font-face{{font-family:"MiSans";src:url("assets/fonts/MiSans-Heavy.ttf");font-weight:900}}
@font-face{{font-family:"Jiezou";src:url("assets/fonts/HYJieZouHeiF.ttf")}}
@font-face{{font-family:"PuHui";src:url("assets/fonts/PuHui-SemiBold.ttf");font-weight:600}}
#root{{font-family:"PuHui",sans-serif;font-weight:600;color:#fff}}
u{{text-decoration:none;font-family:"MiSans";font-weight:900}}
.scrim{{position:absolute;left:0;right:0;bottom:0;height:320px;background:linear-gradient(to bottom,rgba(0,0,0,0),rgba(0,0,0,.72))}}
.scene{{position:absolute;inset:0;background:#07090f;overflow:hidden;outline:8px solid #07090f}}
.aur{{position:absolute;inset:0;background:radial-gradient(900px 620px at 18% 12%,rgba(45,212,191,.20),transparent 70%),radial-gradient(1000px 700px at 88% 92%,rgba(99,102,241,.22),transparent 70%)}}
.aur.a2{{background:radial-gradient(1000px 700px at 82% 10%,rgba(99,102,241,.22),transparent 70%),radial-gradient(800px 600px at 8% 90%,rgba(45,212,191,.18),transparent 70%)}}
.aur.a3{{background:radial-gradient(1200px 800px at 50% 110%,rgba(45,212,191,.22),transparent 70%)}}
.aur.red{{background:radial-gradient(1000px 700px at 80% 15%,rgba(255,107,107,.18),transparent 70%),radial-gradient(900px 650px at 10% 90%,rgba(99,102,241,.2),transparent 70%)}}
.pt{{position:absolute;left:0;right:0;top:78px;text-align:center;font:400 56px/1.2 "Jiezou";letter-spacing:3px;color:#fff}}
.pt small{{display:block;margin-top:14px;font:600 28px/1 "PuHui";color:rgba(255,255,255,.55);letter-spacing:1px}}

.rain{{position:absolute;inset:-40% 0 0 0;display:flex;justify-content:space-between;padding:0 30px;opacity:.09;pointer-events:none}}
.rain i{{font:500 22px/1.25 "JetBrains Mono",ui-monospace,monospace;color:{A};font-style:normal;writing-mode:vertical-rl;text-orientation:upright;letter-spacing:2px}}
.ytf{{position:absolute;left:120px;top:78px;width:1420px;height:799px;box-sizing:border-box;outline:2px solid rgba(60,255,160,.75);outline-offset:6px;box-shadow:0 0 70px rgba(60,255,160,.22);background:#000}}
.ytbar{{position:absolute;left:112px;top:22px;display:flex;align-items:center;gap:14px;font:500 26px/1 "JetBrains Mono",ui-monospace,monospace;color:{A}}}
.ytbar i{{width:16px;height:16px;border-radius:50%;background:#ff3b6b;box-shadow:0 0 14px #ff3b6b}}
.ytbar span{{font:600 28px/1 "PuHui";color:#fff;margin-left:10px}}
.ytv{{position:absolute;left:120px;top:78px;width:1420px;height:799px;object-fit:cover;z-index:7;background:#000}}
.cntl{{position:relative;width:230px;height:230px;margin:0 auto 34px}}.cntl img{{width:230px;height:230px;display:block;filter:drop-shadow(0 0 40px rgba(243,186,47,.45))}}.cnt .cntl svg{{position:absolute;right:-46px;bottom:-22px;width:96px;height:96px;margin:0;background:#07090f;border-radius:50%}}
.xw{{position:absolute;left:370px;top:96px;width:1180px;height:584px;border-radius:20px;overflow:hidden;background:#15202b;box-shadow:0 0 70px rgba(60,255,160,.22),0 40px 100px rgba(0,0,0,.6);outline:2px solid rgba(60,255,160,.7)}}.xw img{{position:absolute;left:0;top:0;width:1180px;height:auto}}.xh{{position:absolute;background:rgba(60,255,160,.34);border-bottom:3px solid {A};transform-origin:0 50%;border-radius:3px}}
.xb{{position:absolute;left:50%;top:716px;transform:translateX(-50%);padding:16px 30px;border-radius:16px;background:rgba(9,12,18,.94);border:1.5px solid {A};font:600 34px/1 "PuHui";color:#fff;white-space:nowrap}}.xb em{{font-style:normal;color:{A}}}
.scan{{position:absolute;inset:0;background:repeating-linear-gradient(to bottom,rgba(255,255,255,.035) 0 1px,transparent 1px 4px);pointer-events:none}}
.cur{{display:inline-block;width:.5em;color:{A};margin-left:6px}}
.demo{{position:absolute;left:70px;bottom:60px;font:600 22px/1 "PuHui";color:rgba(255,255,255,.45);border:1px solid rgba(255,255,255,.2);padding:8px 14px;border-radius:8px}}
/* side cards on the wall */
.side{{position:absolute;top:0;bottom:190px;width:720px;display:flex;align-items:center;z-index:5}}
.sL{{left:64px;justify-content:flex-start}}.sR{{right:64px;justify-content:flex-end}}
.stack{{display:flex;flex-direction:column;align-items:stretch;gap:14px;width:max-content;min-width:470px}}
.tile{{height:98px;box-sizing:border-box;border-radius:24px;background:rgba(9,12,18,.88);border:1.5px solid rgba(255,255,255,.24);display:flex;align-items:center;gap:18px;padding:0 30px;color:#fff;box-shadow:0 16px 44px rgba(0,0,0,.4)}}
.tile span{{white-space:nowrap}}
.tile svg{{width:42px;height:42px;flex:none;color:{A}}}.tile span{{font:400 44px/1 "Jiezou";letter-spacing:2px}}.tile u{{font-size:44px}}
.by{{display:flex;align-items:center;justify-content:center;gap:12px;height:56px;padding:0 18px;margin-top:6px;border-radius:999px;background:rgba(9,12,18,.88);border:1.5px solid rgba(60,255,160,.6);font:600 27px/1 "PuHui"}}
.kin{{display:flex;flex-direction:column;align-items:flex-start;gap:14px;padding:30px 38px;border-radius:24px;background:rgba(9,12,18,.88);border:1.5px solid rgba(60,255,160,.5);box-shadow:0 0 50px rgba(60,255,160,.18),0 18px 50px rgba(0,0,0,.4)}}
.kin span{{font:400 76px/1.12 "Jiezou";letter-spacing:3px;color:{A}}}.kin span u{{font-size:76px}}
.kin small{{font:600 29px/1.35 "PuHui";color:#fff;max-width:460px}}
.kwb .kin span{{font-size:96px}}.kwb .kin span u{{font-size:96px}}
.kin.danger{{border-color:rgba(255,107,107,.6);box-shadow:0 0 50px rgba(255,107,107,.18),0 18px 50px rgba(0,0,0,.4)}}.kin.danger span{{color:{R}}}
.klg{{height:56px;max-width:220px;object-fit:contain}}
.kin svg.big{{width:64px;height:64px;color:{A}}}
.term{{width:520px;border-radius:18px;overflow:hidden;background:#0b0f16;border:1.5px solid rgba(60,255,160,.45);box-shadow:0 20px 60px rgba(0,0,0,.5)}}
.term .tb{{height:40px;background:#161a22;display:flex;align-items:center;gap:8px;padding-left:16px}}.term .tb i{{width:12px;height:12px;border-radius:50%}}
.term pre{{margin:0;padding:22px 26px;font:500 26px/1.6 "JetBrains Mono",ui-monospace,monospace;color:{A};white-space:pre-wrap;min-height:220px}}
/* teaser: cinematic */
.lbox{{position:absolute;left:0;right:0;height:120px;background:#000;z-index:4}}.lbt{{top:0}}.lbb{{bottom:0}}
.tchest{{position:absolute;left:0;right:0;top:640px;text-align:center;z-index:6}}
.tchest span{{display:inline-block;font:400 120px/1.05 "Jiezou";letter-spacing:6px;color:#fff;text-shadow:0 6px 30px rgba(0,0,0,.65)}}
.tchest small{{display:block;margin-top:16px;font:600 34px/1 "PuHui";letter-spacing:8px;color:{A}}}
.tchest .sweep{{position:absolute;inset:0;background:linear-gradient(100deg,transparent 35%,rgba(255,255,255,.55) 50%,transparent 65%);mix-blend-mode:overlay}}
.tz{{position:absolute;left:48px;top:40px;z-index:8}}
.tzb{{display:inline-block;font:400 150px/1 "Jiezou";letter-spacing:4px;color:#BFE3FF;-webkit-text-stroke:14px #111;paint-order:stroke fill;text-shadow:0 10px 0 #111;transform-origin:0 50%}}
.tzs{{margin:18px 0 0 10px;display:inline-block;padding:10px 22px;border-radius:12px;background:#111;font:400 44px/1 "Jiezou";letter-spacing:2px;color:#fff}}
.tlabel{{position:absolute;top:150px;left:64px;z-index:7}}
.tlabel span{{display:inline-flex;align-items:center;gap:12px;padding:12px 24px;border-radius:999px;background:rgba(9,12,18,.86);border:1.5px solid rgba(60,255,160,.6);font:400 36px/1 "Jiezou";letter-spacing:2px}}
.tlabel b{{color:{A};font-weight:400}}
/* web scene */
.persp{{position:absolute;inset:0;perspective:1800px;display:flex;justify-content:center;padding-top:60px;padding-right:160px;box-sizing:border-box}}
.bw{{width:1260px;height:760px;border-radius:18px;overflow:hidden;background:#fff;outline:1px solid rgba(255,255,255,.22);box-shadow:0 50px 120px rgba(0,0,0,.65);position:relative}}
.tb{{height:44px;background:#1b1e26;display:flex;align-items:center;gap:9px;padding-left:18px}}.tb i{{width:13px;height:13px;border-radius:50%}}.tb span{{margin-left:14px;font-size:20px;color:#b9bdc7}}
.wv2{{position:absolute;left:0;right:0;top:44px;bottom:0;overflow:hidden}}.wv2 img{{position:absolute;max-width:none}}
.hl{{position:absolute;background:rgba(60,255,160,.36);border-bottom:3px solid {A};transform-origin:0 50%;border-radius:3px}}
.wlg{{position:absolute;left:70px;top:70px;padding:14px 18px;border-radius:24px;background:#10141d;border:1.5px solid rgba(255,255,255,.2);box-shadow:0 20px 60px rgba(0,0,0,.6)}}.wlg img{{height:84px;display:block}}
.wbd{{position:absolute;right:110px;top:744px;padding:18px 34px;border-radius:18px;background:rgba(9,12,18,.94);border:1.5px solid {A};font:600 34px/1 "PuHui";box-shadow:0 0 40px rgba(60,255,160,.25)}}.wbd em{{font-style:normal;color:{A}}}
/* glass node graph */
.gn{{position:absolute;width:300px;padding:26px 22px;box-sizing:border-box;border-radius:22px;text-align:center;background:rgba(255,255,255,.04);border:1.5px solid rgba(255,255,255,.16);color:rgba(255,255,255,.55)}}
.gn svg{{width:76px;height:76px;color:rgba(255,255,255,.6);display:block;margin:0 auto 14px}}
.gn b{{display:block;font:400 36px/1.15 "Jiezou";letter-spacing:1px;color:inherit;font-weight:400;white-space:nowrap}}.gn b u{{font-size:36px}}
.gn small{{display:block;margin-top:10px;font:600 24px/1.3 "PuHui";color:rgba(255,255,255,.5)}}
.ge{{position:absolute;height:3px;transform-origin:0 50%;background:rgba(255,255,255,.18);border-radius:2px}}
.gn.on{{color:#fff}}
.pk{{position:absolute;left:0;top:0;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:{A};box-shadow:0 0 24px {A},0 0 60px {A};opacity:0;z-index:3}}
/* lists / rows in scenes */
.rows{{position:absolute;left:330px;right:330px;top:230px;display:flex;flex-direction:column;gap:20px}}
.rw{{display:flex;justify-content:space-between;align-items:center;padding:26px 36px;border-radius:18px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.2);font:400 46px/1 "Jiezou";letter-spacing:2px}}
.rw small{{font:600 28px/1 "PuHui";color:rgba(255,255,255,.55);letter-spacing:0}}.rw em{{font-style:normal;color:{A}}}
.rl{{display:flex;align-items:center;gap:22px}}.rl img{{width:64px;height:64px;border-radius:50%}}
.rw.tot{{border-color:{A};box-shadow:0 0 40px rgba(60,255,160,.25)}}
.bars{{position:absolute;left:220px;right:220px;top:300px}}
.br{{margin-bottom:56px}}.br label{{display:block;font:600 32px/1 "PuHui";color:rgba(255,255,255,.7);margin-bottom:18px}}
.bk{{display:flex;align-items:center;gap:26px}}.bk i{{display:block;height:110px;border-radius:16px;transform-origin:0 50%}}.bk span{{font:400 72px/1 "Jiezou";letter-spacing:2px}}
.bigx{{position:absolute;right:240px;top:170px;font:400 150px/1 "Jiezou";color:{A}}}
.ev{{position:absolute;left:60px;right:60px;top:220px;display:flex;justify-content:center;gap:28px}}
.evc h5{{margin:0 0 16px;font:400 36px/1 "Jiezou";letter-spacing:2px;color:{A};font-weight:400}}
.cc{{position:relative;overflow:hidden;border-radius:14px;background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.5)}}.cc img{{position:absolute;max-width:none}}
.cnt{{position:absolute;left:0;right:0;top:130px;text-align:center}}.cnt svg{{width:170px;height:170px;color:{A};display:block;margin:0 auto 36px}}.cnt b{{font:400 210px/1 "Jiezou";color:{A};font-weight:400}}.cnt b u{{font-size:210px}}.cnt span{{display:block;margin-top:30px;font:600 40px/1.3 "PuHui";color:#fff}}
'''


class B:
    def __init__(s, ctx):
        s.under = []; s.c = ctx; s.clips = []; s.js = []; s.audio = []; s.cam = []; s.pushes = []; s.n = 0; s.side = 'R'

    def id(s, p='b'):
        s.n += 1; return f'{p}{s.n}'
    def S(s, n, off=0.0): return s.c['T'](s.c['LS'][n]) + off
    def Ee(s, n, off=0.0): return s.c['T'](s.c['LE'][n]) + off
    def W(s, n, kw, off=0.0): return s.c['word_time'](n, kw) + off
    def add(s, h, st, en, tr):
        s.clips.append(h.replace('§', f'data-start="{st:.3f}" data-duration="{max(en - st, .04):.3f}" data-track-index="{tr}"'))

    SX = {'click': ('1133', .34, .40), 'whoosh': ('3115', .56, .32), 'spark': ('3060', 1.2, .40), 'ping': ('3124', .5, .36),
          'glow': ('3083', 2.3, .26), 'pop': ('3005', .18, .38), 'hit': ('833', 1.0, .38), 'swish': ('1487', .6, .30), 'bounce': ('2358', .4, .30)}
    def sfx(s, t, k):
        f, d, v = s.SX[k]
        s.audio.append(f'<audio id="{s.id("fx")}" src="assets/sfx2/{f}.mp3" data-start="{t:.3f}" data-duration="{d}" data-track-index="{40 + s.n % 4}" data-volume="{v}"></audio>')

    def fade(s, i, sel, t, y=26, dur=.45, ease='power3.out'):
        s.js.append(f'tl.fromTo("#{i} {sel}",{{opacity:0,y:{y}}},{{opacity:1,y:0,duration:{dur},ease:"{ease}"}},{t:.3f});')

    def nextside(s):
        s.side = 'L' if s.side == 'R' else 'R'; return s.side

    # ---------- A-roll side cards ----------
    def _side(s, st, en, inner, extra_cls='', snd='ping'):
        sd = s.nextside(); i = s.id('sd'); dx = -60 if sd == 'L' else 60
        s.add(f'<div id="{i}" class="clip side s{sd} {extra_cls}" §>{inner}</div>', st, en, 8)
        s.cam.append((st, en, sd))
        return i, dx

    def kw(s, st, en, text, sub=None, logo=None, icon=None, big=False, danger=False, count=None):
        lg = f'<img class="klg" src="assets/logos/{logo}">' if logo else (svg(icon, 'big') if icon else '')
        sb = f'<small>{sub}</small>' if sub else ''
        i, dx = s._side(st, en, f'<div class="kin{" danger" if danger else ""}">{lg}<span class="kt">{jz(text).replace(chr(10), "<br>")}</span>{sb}</div>', 'kwb' if big else '')
        s.js.append(f'tl.fromTo("#{i} .kin",{{opacity:0,x:{dx}}},{{opacity:1,x:0,duration:.55,ease:"power3.out"}},{st + .05:.3f});')
        if count:
            v, dec, pre, suf = count
            s.js.append(f'(function(){{const o={{v:0}};const el=document.querySelector("#{i} .kt");tl.to(o,{{v:{v},duration:1.2,ease:"power2.out",'
                        f'onUpdate:()=>{{el.textContent="{pre}"+o.v.toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})+"{suf}";}}}},{st + .2:.3f});}})();')
            s.sfx(st + .2, 'glow')
        else:
            s.sfx(st, 'ping')
        return i

    def tiles(s, st, en, items, by=None, by_t=None):
        t = ''.join(f'<div class="tile t{k}">{svg(ic)}<span>{jz(w)}</span></div>' for k, (w, ic, _) in enumerate(items))
        b = f'<div class="by">{by}</div>' if by else ''
        i, dx = s._side(st, en, f'<div class="stack">{t}{b}</div>')
        for k, (_, _, tm) in enumerate(items):
            s.js.append(f'tl.fromTo("#{i} .t{k}",{{opacity:0,x:{dx},scale:.94}},{{opacity:1,x:0,scale:1,duration:.42,ease:"back.out(1.5)"}},{tm:.3f});'); s.sfx(tm, 'click')
        if by:
            s.js.append(f'tl.to("#{i} .tile",{{borderColor:"{A}",boxShadow:"0 0 26px rgba(60,255,160,.32)",duration:.35,stagger:.04}},{by_t:.3f});')
            s.js.append(f'tl.fromTo("#{i} .by",{{opacity:0,y:16}},{{opacity:1,y:0,duration:.45,ease:"power3.out"}},{by_t:.3f});'); s.sfx(by_t, 'glow')
        return i

    def terminal(s, st, en, lines, title='terminal'):
        body = ''.join(f'<div class="tl{k}" style="opacity:0">{E(x)}</div>' for k, x in enumerate(lines))
        i, dx = s._side(st, en, f'<div class="term"><div class="tb"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i><span>{title}</span></div><pre>{body}</pre></div>')
        s.js.append(f'tl.fromTo("#{i} .term",{{opacity:0,x:{dx}}},{{opacity:1,x:0,duration:.5,ease:"power3.out"}},{st + .05:.3f});')
        for k in range(len(lines)):
            s.js.append(f'tl.to("#{i} .tl{k}",{{opacity:1,duration:.08}},{st + .5 + k * .45:.3f});'); s.sfx(st + .5 + k * .45, 'click')
        return i

    def push(s, st, en, a=1.0, b=1.08):
        s.pushes.append((st, en, a, b))

    # ---------- full dark scenes ----------
    def scene(s, st, en, body, aur='', snd='whoosh'):
        import random
        rnd = random.Random(int(st * 1000))
        cols = ''.join('<i>' + ''.join(rnd.choice('0123456789ABCDEF') for _ in range(60)) + '</i>' for _ in range(28))
        i = s.id('sc'); s.add(f'<div id="{i}" class="clip scene" §><div class="aur {aur}"></div><div class="rain">{cols}</div>{body}<div class="scan"></div></div>', st, en, 6)
        s.js.append(f'tl.fromTo("#{i} .rain",{{y:0}},{{y:{min(60 * (en - st), 420):.0f},duration:{en - st:.2f},ease:"none"}},{st:.3f});')
        if '<div class="pt">' in body:
            s.js.append(f'tl.fromTo("#{i} .pt",{{opacity:0,x:-14}},{{opacity:1,x:0,duration:.06}},{st + .02:.3f});')
            for k, (x, sh) in enumerate(((10, '-4px 0 #ff3b6b,4px 0 #3cffa0'), (-6, '3px 0 #ff3b6b,-3px 0 #3cffa0'), (0, 'none'))):
                s.js.append(f'tl.set("#{i} .pt",{{x:{x},textShadow:"{sh}"}},{st + .08 + k * .07:.3f});')
            s.js.append(f'tl.to("#{i} .pt .cur",{{opacity:0,duration:.01,repeat:{int((en - st) / .5)},yoyo:true,repeatDelay:.49}},{st + .3:.3f});')
        if snd: s.sfx(st, snd)
        return i

    def web(s, shot, st, en, crop=None, rects=None, logo=None, badge=None, badge_t=None, dom=None, hl_t=None, ih=900):
        m = SH[shot]; rs = rects if rects is not None else (m.get('rects') or [])
        if crop is None:
            r = rs[0] if rs else None
            if r and (shot.startswith('bn_sq') or shot == 'blockaid_sq'):
                cx, cw, cy = max(min(rr['x'] for rr in rs[:3]) - 24, 0), 760, max(min(rr['y'] for rr in rs[:3]) - 230, 0)   # article column
            elif r:
                cw = max(r['w'] + 260, 760); cx = min(max(r['x'] - 120, 0), 1440 - cw); cy = max(r['y'] - 240, 0)
            else:
                cx, cy, cw = 0, 0, 1440
        else:
            cx, cy, cw = crop
        sc = 1260 / cw
        hl = ''.join(f'<div class="hl" style="left:{r["x"] * sc - cx * sc - 6:.0f}px;top:{r["y"] * sc - cy * sc - 4:.0f}px;width:{r["w"] * sc + 12:.0f}px;height:{r["h"] * sc + 8:.0f}px"></div>' for r in rs[:3])
        d = dom or m['url'].split('/')[2]
        lg = f'<div class="wlg"><img src="assets/logos/{logo}"></div>' if logo else ''
        bd = f'<div class="wbd">{badge}</div>' if badge else ''
        i = s.scene(st, en, f'<div class="persp"><div class="bw"><div class="tb"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i><span>{E(d)}</span></div><div class="wv2"><img src="assets/shots/{shot}.png" style="left:{-cx * sc:.0f}px;top:{-cy * sc:.0f}px;width:{1440 * sc:.0f}px;height:{ih * sc:.0f}px">{hl}</div></div>{lg}{bd}</div>', 'a3')
        s.js.append(f'tl.fromTo("#{i} .bw",{{rotateY:-20,rotateX:9,y:60,opacity:0,scale:.9}},{{rotateY:-6,rotateX:3,y:0,opacity:1,scale:1,duration:.8,ease:"power3.out"}},{st + .03:.3f});')
        s.js.append(f'tl.to("#{i} .bw",{{rotateY:0,rotateX:0,scale:1.06,duration:{max(en - st - .85, .5):.2f},ease:"power1.inOut"}},{st + .82:.3f});')
        if logo: s.js.append(f'tl.fromTo("#{i} .wlg",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.45,ease:"back.out(1.8)"}},{st + .45:.3f});')
        if hl:
            t = hl_t or min(st + 1.0, en - .8)
            s.js.append(f'tl.fromTo("#{i} .hl",{{scaleX:0}},{{scaleX:1,duration:.5,stagger:.2,ease:"power2.out"}},{t:.3f});'); s.sfx(t, 'ping')
        if badge:
            t = badge_t or st + 1.4
            s.js.append(f'tl.fromTo("#{i} .wbd",{{opacity:0,y:18}},{{opacity:1,y:0,duration:.4,ease:"back.out(1.6)"}},{t:.3f});'); s.sfx(t, 'pop')
        return i

    def yt(s, st, en, cuts, src):
        """real news footage in a monitor frame above the subtitles; cuts = [(clip, media_start, seconds)]"""
        en = min(en, st + sum(c[2] for c in cuts))
        i = s.scene(st, en, f'<div class="ytbar"><i></i>REC<span>畫面來源：{E(src)}</span></div><div class="ytf"></div>', 'a3')
        s.js.append(f'tl.to("#{i} .ytbar i",{{opacity:.2,duration:.5,repeat:{int((en - st) / .5)},yoyo:true}},{st:.3f});')
        t = st
        for clip, ms, d in cuts:
            d = min(d, en - t)
            if d < .2: break
            v = s.id('yv')
            s.add(f'<video id="{v}" class="clip ytv" src="assets/yt/{clip}.mp4" muted playsinline data-media-start="{ms:.3f}" §></video>', t, t + d, 7)
            s.js.append(f'tl.fromTo("#{v}",{{opacity:0,scale:1.025}},{{opacity:1,scale:1,duration:.2,ease:"power2.out"}},{t + .02:.3f});')
            t += d
        return i

    def graph(s, st, en, title, nodes, edges, sub='', aur='', demo=None):
        """nodes: [(key,x,y,icon,label,small,t_on,danger)]  edges: [(a,b,t_on)]"""
        pos = {k: (x, y) for k, x, y, *_ in nodes}; parts = []
        for k, (a, b, t) in enumerate(edges):
            (x1, y1), (x2, y2) = pos[a], pos[b]; L = math.hypot(x2 - x1, y2 - y1); ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
            parts.append(f'<div class="ge e{k}" style="left:{x1}px;top:{y1}px;width:{L:.0f}px;transform:rotate({ang:.1f}deg)"></div>')
        for k, (key, x, y, ic, lab, sm, t, dg) in enumerate(nodes):
            parts.append(f'<div class="gn n{k}" style="left:{x}px;top:{y}px">{svg(ic)}<b>{jz(lab)}</b>{f"<small>{sm}</small>" if sm else ""}</div>')
        dm = f'<div class="demo">{demo}</div>' if demo else ''
        i = s.scene(st, en, f'<div class="pt">{jz(title)}<span class="cur">_</span>{f"<small>{sub}</small>" if sub else ""}</div>{"".join(parts)}{dm}<div class="pk"></div>', aur)
        s.js.append(f'tl.set("#{i} .gn",{{xPercent:-50,yPercent:-50}},{st:.3f});')
        s.js.append(f'tl.fromTo("#{i} .gn",{{opacity:0,y:24,xPercent:-50,yPercent:-50}},{{opacity:.55,y:0,xPercent:-50,yPercent:-50,duration:.45,stagger:.05,ease:"power3.out"}},{st + .05:.3f});')
        s.js.append(f'tl.fromTo("#{i} .ge",{{scaleX:0}},{{scaleX:1,duration:.5,stagger:.05,ease:"power2.out"}},{st + .15:.3f});')
        for k, (key, x, y, ic, lab, sm, t, dg) in enumerate(nodes):
            if t is None: continue
            c = R if dg else A; rgb = '255,107,107' if dg else '60,255,160'
            s.js.append(f'tl.to("#{i} .n{k}",{{opacity:1,scale:1.05,color:"#ffffff",borderColor:"{c}",backgroundColor:"rgba({rgb},.08)",boxShadow:"0 0 50px rgba({rgb},.35)",duration:.45,ease:"power3.out"}},{t:.3f});')
            s.js.append(f'tl.to("#{i} .n{k} svg",{{color:"{c}",duration:.3}},{t:.3f});')
            s.sfx(t, 'spark' if k == 0 else 'click')
        lit = sorted([(t, x, y) for (key, x, y, ic, lab, sm, t, dg) in nodes if t is not None])
        if len(lit) >= 2:
            t0, x0, y0 = lit[0]
            s.js.append(f'tl.set("#{i} .pk",{{x:{x0},y:{y0},opacity:1}},{t0:.3f});')
            for (ta, xa, ya), (tb, xb, yb) in zip(lit, lit[1:]):
                d = max(min(tb - ta, .6), .15)
                s.js.append(f'tl.to("#{i} .pk",{{x:{xb},y:{yb},duration:{d:.2f},ease:"power2.inOut"}},{tb - d:.3f});')
            s.js.append(f'tl.to("#{i} .pk",{{opacity:0,duration:.3}},{min(lit[-1][0] + 1.0, en - .3):.3f});')
        for k, (a, b, t) in enumerate(edges):
            if t is None: continue
            dg = next(n[7] for n in nodes if n[0] == b)
            s.js.append(f'tl.to("#{i} .e{k}",{{backgroundColor:"{R if dg else A}",duration:.3}},{t:.3f});')
        return i

    def rows(s, st, en, title, items, total=None, sub='', aur=''):
        """items: [(t,left,right,small[,logo])]"""
        h = ''.join(f'<div class="rw r{k}"><span class="rl">{f"<img src=assets/logos/{it[4]}>" if len(it) > 4 else ""}{jz(it[1])}</span><span><em>{E(it[2])}</em> <small>{E(it[3])}</small></span></div>' for k, it in enumerate(items))
        if total: h += f'<div class="rw tot rt"><span>{jz(total[1])}</span><span><em>{E(total[2])}</em></span></div>'
        i = s.scene(st, en, f'<div class="pt">{jz(title)}<span class="cur">_</span>{f"<small>{sub}</small>" if sub else ""}</div><div class="rows">{h}</div>', aur)
        for k, it in enumerate(items): s.fade(i, f'.r{k}', it[0], 20); s.sfx(it[0], 'click')
        if total: s.fade(i, '.rt', total[0], 20); s.sfx(total[0], 'glow')
        return i


def build(ctx):
    b = B(ctx); S, Ee, W = b.S, b.Ee, b.W
    D1, TEASE = ctx['D1'], ctx['TEASE']

    # ===== teasers: channel style — pink gingham frame, presenter inset, big 精彩預告 =====
    b.under = [f'<div id="pinkbg" class="clip" style="position:absolute;inset:0;background:url(assets/pink.png) center/cover" data-start="0" data-duration="{TEASE:.3f}" data-track-index="0"></div>']
    b.js.append(f'tl.set("#cam",{{scale:.92,x:0,y:43}},0);tl.set("#cam",{{scale:1,x:0,y:0}},{TEASE:.3f});')
    for n, (st, en, tag) in enumerate(((0, D1, '3分钟搬走25亿'), (D1, TEASE, '史上最大黑客案')), 1):
        i = b.id('tz')
        b.add(f'<div id="{i}" class="clip tz" §><div class="tzb">{jz("精彩预告")}</div><div class="tzs">{jz(tag)}</div></div>', st, en, 7)
        b.js.append(f'tl.fromTo("#{i} .tzb",{{scale:.4,opacity:0,rotation:-8}},{{scale:1,opacity:1,rotation:-3,duration:.45,ease:"back.out(2)"}},{st + .05:.3f});')
        b.fade(i, '.tzs', st + .35, 16); b.sfx(st + .05, 'hit')

    # ===== Hook =====
    b.yt(max(S(2, .2), Ee(2) - 5.2), Ee(2), [('cnn_10', .2, 5.2)], 'CNN')
    b.web('bn_sq_634', W(3, '币安公布'), Ee(3), logo='binance_mark.png', badge='11/03 官方公布：<em>完整攻擊流程</em>', badge_t=W(3, '整个流程'))
    b.terminal(S(4, .1), Ee(4), ['> scan binance_hack', '> sources: 5', '> trace: started ...'], 'YOMI@research')
    i = b.scene(S(5), Ee(5), '<div class="pt">我扒了所有公開資料<small>官方報告 · 執法機構 · 鏈上分析</small></div><div class="ev">'
                + ''.join(f'<div class="evc e{k}"><h5>{h}</h5><div class="cc" style="width:330px;height:420px"><img src="assets/shots/{sh}.png" style="left:{-x * .62:.0f}px;top:{-y * .62:.0f}px;width:{1440 * .62:.0f}px;height:{900 * .62:.0f}px"></div></div>'
                          for k, (h, sh, x, y) in enumerate((('幣安報告', 'bn_sq_634', 200, 60), ('FBI', 'fbi', 0, 230), ('TRM Labs', 'trm', 330, 120), ('Elliptic', 'elliptic_launder', 40, 200), ('Blockaid', 'blockaid_sq', 200, 160))))
                + '</div>')
    for k in range(5): b.fade(i, f'.e{k}', S(5, .3 + k * .45), 30); b.sfx(S(5, .3 + k * .45), 'click')
    b.tiles(S(6), Ee(7), [('从哪里进来', 'search', W(6, '黑客到底')), ('授权怎么来', 'pen', W(6, '又怎么')), ('钱怎么转走', 'coins', S(7, .2))])

    # ===== attack chain overview =====
    Y1, Y2 = 470, 790
    nodes = [('a', 260, Y1, 'tool', '开发工具', '', W(10, '被篡改'), True),
             ('b', 610, Y1, 'brief', '假 HR', '', W(11, '伪装'), True),
             ('c', 960, Y1, 'cpu', 'AI 工具', '', W(12, 'AI工具'), True),
             ('d', 1310, Y1, 'key', '部署凭证', '', W(12, '窃取'), True),
             ('e', 1660, Y1, 'lock', '签名服务', '', W(12, '签名服务'), True),
             ('f', 1660, Y2, 'coins', '热钱包', '', S(13, .2), True),
             ('g', 1310, Y2, 'file', 'EIP-7702', '', W(13, 'EIP'), True)]
    edges = [('a', 'b', W(11, '伪装')), ('b', 'c', W(12, 'AI工具')), ('c', 'd', W(12, '窃取')), ('d', 'e', W(12, '签名服务')), ('e', 'f', S(13, .2)), ('f', 'g', W(13, 'EIP'))]
    b.graph(S(9), Ee(13), '攻击链全貌', nodes, edges, '2026/06 → 10/29', 'red')

    # ===== event analysis =====
    b.yt(S(15), Ee(15), [('cnn_30', .5, 7.3)], 'CNN')
    i = b.scene(S(16), Ee(16), f'<div class="pt">规模有多大<small>對比去年 Bybit 被盜</small></div><div class="bars"><div class="br"><label>Bybit · 2025 年 2 月</label><div class="bk"><i class="ba" style="width:{1480 * 1.46 / 6.34:.0f}px;background:#4a5262"></i><span>$14.6 亿</span></div></div>'
                f'<div class="br"><label><img src=assets/logos/bnb.png style="width:40px;height:40px;vertical-align:middle;margin-right:12px">幣安 · 2026 年 10 月</label><div class="bk"><i class="bb" style="width:1180px;background:{A}"></i><span class="bbt">$63.4 亿</span></div></div></div><div class="bigx">×4.3</div>', 'a2')
    b.js.append(f'tl.fromTo("#{i} .ba",{{scaleX:0}},{{scaleX:1,duration:.7,ease:"power3.out"}},{W(16, "当时"):.3f});'); b.sfx(W(16, '当时'), 'click')
    b.js.append(f'tl.fromTo("#{i} .bb,#{i} .bbt",{{scaleX:0,opacity:0}},{{scaleX:1,opacity:1,duration:1.0,ease:"power3.out"}},{W(16, "而这次"):.3f});'); b.sfx(W(16, '而这次'), 'swish')
    b.fade(i, '.bigx', W(16, '四倍'), 30); b.sfx(W(16, '四倍'), 'hit')
    b.web('bn_sq_multistage', S(17), Ee(17), logo='binance_mark.png', badge='不是一次入侵，是<em>多階段</em>攻擊', badge_t=W(17, '整个流程'))
    b.kw(W(18, '签名服务'), Ee(18), '签名服务\n已被入侵', icon='lock', danger=True)
    t19 = S(19) + (Ee(19) - S(19)) * .5
    i = b.scene(S(19), t19, f'<div class="cnt"><div class="cntl"><img src="assets/logos/binance_mark.png">{svg("pause")}</div><b>{jz("暂停提币")}</b><span>幣安 2026-10-30 公告：暫停提現、檢查安全</span></div>', 'a2')
    b.js.append(f'tl.fromTo("#{i} .cnt svg",{{scale:.4,opacity:0}},{{scale:1,opacity:1,duration:.5,ease:"back.out(1.7)"}},{S(19, .1):.3f});')
    b.fade(i, '.cnt b', S(19, .4)); b.fade(i, '.cnt span', S(19, .9), 14); b.sfx(S(19, .4), 'hit')
    i = b.scene(t19, Ee(19), '<div class="xw"><img src="assets/shots/x_suspend.png"><div class="xh" style="left:347px;top:258px;width:603px;height:50px"></div><div class="xh" style="left:33px;top:310px;width:438px;height:50px"></div></div><div class="xb">幣安官方 X · 2026/10/30：<em>充值、提現暫停</em></div>', 'a3')
    b.js.append(f'tl.fromTo("#{i} .xw",{{y:40,opacity:0,scale:.94}},{{y:0,opacity:1,scale:1,duration:.5,ease:"power3.out"}},{t19 + .03:.3f});')
    b.js.append(f'tl.fromTo("#{i} .xh",{{scaleX:0}},{{scaleX:1,duration:.4,stagger:.25,ease:"power2.out"}},{t19 + .6:.3f});'); b.sfx(t19 + .6, 'ping')
    b.fade(i, '.xb', t19 + 1.0, 14)

    # ===== June: engineer A =====
    b.kw(S(20), Ee(20), '2026 年 6 月', '事情要從這裡說起', icon='clock')
    b.kw(W(21, '工程师a'), Ee(21), '工程师 A', '錢包運維工程師', icon='users')
    b.web('brew', S(22, .3), Ee(23), crop=(0, 0, 1440), dom='brew.sh', logo='brew.svg', badge='macOS 常見的工具管理軟體', badge_t=S(23, .3))
    b.graph(S(24), Ee(24), '安装程序被动了手脚', [('p', 700, 560, 'pkg', 'Homebrew 安装程序', '看起來正常', S(24, .1), False),
                                                 ('m', 1220, 560, 'code', '黑客植入的代码', '', W(24, '提前'), True)], [('p', 'm', W(24, '提前'))], aur='red', demo='示意')
    b.tiles(S(25), Ee(26), [('发现异常', 'eye', W(25, '发现')), ('换设备 换凭据', 'check', W(25, '换了设备')), ('为什么还被盗', 'alert', W(26, '怎么'))])
    b.graph(S(27), Ee(27), '6 月就泄露的信息', [('a', 520, 560, 'users', '工程师 A', '身份 + 同事名單', S(27, .2), False),
                                                ('h', 1400, 560, 'hacker', '黑客', '拿到團隊名單', W(27, '暴露'), True)], [('a', 'h', W(27, '暴露'))], aur='red', demo='示意')
    b.kw(S(28), Ee(30), '潜伏\n4 个月', '6 月拿到資料，10 月才下手', icon='clock', big=True)

    # ===== September: engineer B =====
    b.kw(W(32, '工程师b'), Ee(32), '工程师 B', '另一名軟體工程師', icon='users')
    b.graph(S(33), Ee(35), '9 月：假招聘', [('j', 620, 560, 'brief', '招聘平台上的「HR」', '偽裝身份', W(33, '求职平台'), True),
                                           ('b', 1300, 560, 'users', '工程师 B', '視頻面試 · 社群帳號', W(33, '工程师b'), False)], [('j', 'b', W(33, '冒充'))], aur='red', demo='示意')
    b.graph(S(36), Ee(37), '“面试作业”', [('h', 700, 560, 'file', '面试作业', '程式題', W(36, '面试作业'), False),
                                       ('m', 1220, 560, 'code', '藏着恶意代码', '', W(37, '居然'), True)], [('h', 'm', W(37, '居然'))], aur='red', demo='示意')
    b.graph(S(38), Ee(39), '正常组件被换掉', [('o', 700, 560, 'pkg', '正常开发组件', '', S(38, .3), False),
                                             ('e', 1220, 560, 'alert', '恶意版本', '', W(39, '替换'), True)], [('o', 'e', W(39, '替换'))], aur='red', demo='示意')
    b.web('pyenv', S(40), Ee(41), logo='github.svg', dom='github.com/pyenv/pyenv', badge='管理 Python 版本的開發工具', badge_t=S(40, 1.4))
    b.graph(S(43), Ee(43), '随时可以执行命令', [('pc', 650, 560, 'laptop', '工程师 B 的电脑', '', S(43, .2), True),
                                                ('sv', 1270, 560, 'server', '黑客控制的服务器', '', W(43, '外部服务器'), True)], [('pc', 'sv', W(43, '执行命令'))], aur='red', demo='示意')
    b.web('bn_sq_endpoint', S(44), Ee(45), logo='binance_mark.png', badge='終端安全工具<em>沒有偵測到</em>', badge_t=S(44, 1.6))
    b.push(S(47), Ee(47))
    b.yt(S(47), Ee(47), [('f24_8', .2, 2.0), ('f24_16', .2, 3.0)], 'FRANCE 24')

    # ===== Oct 20 =====
    b.kw(S(48), Ee(48), '10/20', '攻擊出現轉折點', icon='bolt', danger=True)
    b.graph(S(49), Ee(50), '10/20：横向移动', [('b', 330, 560, 'laptop', '工程师 B', '已被入侵', S(49, .2), True),
                                               ('ai', 860, 560, 'cpu', '内部 AI 工具', '當作跳板', W(49, 'AI工具'), True),
                                               ('a', 1420, 380, 'users', '工程师 A', '權限', W(49, '工程师a'), True),
                                               ('c', 1420, 740, 'users', '工程师 C', '權限', W(49, '工程师c'), True)],
            [('b', 'ai', W(49, 'AI工具')), ('ai', 'a', W(49, '工程师a')), ('ai', 'c', W(49, '工程师c'))], '一共轉換了三輪身份', 'red')
    b.kw(S(53), Ee(53), 'AI 是跳板\n不是元凶', '攻擊者利用內部 AI 工具擴大範圍', icon='cpu')
    b.tiles(S(54), Ee(57), [('部署权限 Token', 'key', W(54, 'TOKEN')), ('≠ 钱包私钥', 'x', W(56, '私钥')), ('能做系统部署', 'check', W(57, '部署'))])
    b.graph(S(58), Ee(58), '10/29：触发', [('c', 360, 560, 'laptop', '工程师 C 的电脑', '', S(58, .3), True),
                                          ('ct', 960, 560, 'pkg', '部署容器', '用 A 的憑證', W(58, '部署'), True),
                                          ('sc', 1560, 560, 'alert', '恶意脚本', '被觸發', W(58, '触发'), True)],
            [('c', 'ct', W(58, '部署')), ('ct', 'sc', W(58, '触发'))], '10/29 17:15–19:56 UTC', 'red')
    pipe = [('q', 300, 600, 'chat', '请求', '充值 / 提現', None, False), ('k', 720, 600, 'shield', '权限检查', '', None, False),
            ('s', 1140, 600, 'pen', '签名', '', None, False), ('o', 1560, 600, 'chain', '上链', '', None, False)]
    b.graph(S(59), Ee(60), '交易所内部的一个请求', [(k, x, y, ic, l, sm, W(60, kw_), d) for (k, x, y, ic, l, sm, _, d), kw_ in zip(pipe, ('一个请求', '检查', '签名', '上链'))],
            [('q', 'k', W(60, '检查')), ('k', 's', W(60, '签名')), ('s', 'o', W(60, '上链'))], aur='a2', demo='示意')
    b.web('bn_sq_signing', S(62), Ee(63), logo='binance_mark.png', badge='未授權訪問<em>錢包簽名服務</em>', badge_t=S(63))
    b.kw(W(64, '任何人'), Ee(64), '内部任何人\n都无权使用', icon='lock', danger=True)
    b.graph(S(66), Ee(68), '黑客跳过了权限检查', [('q', 300, 600, 'chat', '请求', '', S(66, .2), False), ('k', 720, 600, 'shield', '权限检查', '被跳過', None, False),
                                                 ('s', 1140, 600, 'pen', '签名服务', '', W(68, '签名服务'), True), ('o', 1560, 600, 'coins', '发起交易', '', W(68, '发起'), True)],
            [('q', 'k', S(67)), ('k', 's', W(68, '跳过')), ('s', 'o', W(68, '发起'))], aur='red', demo='示意')
    b.yt(W(69, '这简直'), Ee(69), [('dw_330', .3, 7.5)], 'DW News')
    b.web('bn_notice_nokey', S(70), Ee(70), logo='binance_mark.png', badge='沒有私鑰洩露的證據，<em>錢卻被轉走</em>', badge_t=S(70, 2.0))
    b.push(S(71), Ee(71), 1.0, 1.08)
    b.yt(S(71), Ee(71), [('dw_180', .3, 7.5)], 'DW News')

    # ===== Oct 29 =====
    b.yt(S(72), Ee(72), [('f24_1', 2.5, 5.4)], 'FRANCE 24')
    b.rows(S(73), Ee(77), '10/29 被转出', [(W(73, '先转出'), 'XRP', '2.3346 亿枚', '20:05 UTC', 'xrp.png'), (W(74, '索拉纳'), 'SOL', '约 97 万枚', '', 'sol.png'),
                                          (W(74, 'optimism'), 'OP', '4,420 万枚', '', 'op.png'), (W(77, '18,270'), 'BTC', '18,270 枚', '', 'btc.png')], sub='來源：幣安初步調查報告', aur='red')
    b.yt(S(78), Ee(78), [('dw_60', 6.1, 2.1)], 'DW News')
    b.web('etherscan_b14', S(79), Ee(79), crop=(0, 255, 900), dom='etherscan.io', logo='etherscan.png', badge='Binance 14：幣安的以太坊熱錢包', badge_t=S(79, 1.0))
    b.tiles(S(80), Ee(81), [('热钱包：在线', 'fire', S(80, .3)), ('处理日常提现', 'coins', W(80, '提现')), ('签名和权限很重要', 'shield', W(81, '签名'))])
    b.kw(W(82, 'EIP'), Ee(83), 'EIP-7702', '以太坊的一個功能', logo='eth.png', big=True)
    b.web('pectra', S(84), Ee(85), logo='eth.png', badge='2025-05-07 隨 Pectra 升級上線', badge_t=S(85))
    b.graph(S(86), Ee(89), '钱包挂上合约代码', [('w', 560, 560, 'wallet', '普通钱包', '', S(86, .2), False),
                                                ('c', 1260, 560, 'code', '智能合约', '部署在鏈上的程式', W(86, '智能合约'), False)], [('w', 'c', W(86, '授权'))], 'EIP-7702：一份有效簽名，授權使用合約代碼', 'a2', demo='示意')
    b.tiles(S(90), Ee(91), [('别人代付手续费', 'gas', W(90, '代付')), ('授权他人操作', 'users', W(90, '设置')), ('被反向使用', 'alert', W(91, '反向'))])
    b.kw(S(92), Ee(93), '一份有效签名', '黑客攻擊的重點，就在這份授權上', icon='pen')
    b.web('blockaid_sq', S(94), Ee(94), badge='Blockaid：黑客<em>提前部署好合約</em>', badge_t=S(94, 2.0))
    b.graph(S(95), Ee(96), '自动归集资产的合约', [('e', 420, 380, 'coins', 'ETH', '', W(96, '以太坊'), False), ('u', 420, 600, 'coins', 'USDT', '', W(96, '多种代币'), False),
                                                  ('o', 420, 820, 'coins', '其他代币', '', W(96, '多种代币', .2), False),
                                                  ('c', 1000, 600, 'code', '归集合约', '', S(95, .2), True), ('h', 1560, 600, 'hacker', '黑客地址', '', W(96, '指定地址'), True)],
            [('e', 'c', W(96, '集中')), ('u', 'c', W(96, '集中')), ('o', 'c', W(96, '集中')), ('c', 'h', W(96, '转移'))], aur='red', demo='示意')
    b.tiles(S(97), Ee(98), [('测试钱包 1', 'wallet', W(98, '几个钱包')), ('测试钱包 2', 'wallet', W(98, '几个钱包', .3)), ('委托→转移 跑通', 'check', W(98, '委托'))])
    b.kw(S(99), Ee(100), '50 份授权', '10/29 晚上 8 點，一筆交易裡塞了 50 份已簽名授權', icon='file', count=(50, 0, '', ' 份'))
    nn = [('cur', 960, 400, 'wallet', '钱包当前 nonce', '一直在變', W(102, 'nonce'), False)]
    nn += [(f'n{k}', 520 + k * 220, 760, 'file', f'#N+{k}', '', W(103, '生效', k * .15), k == 2) for k in range(5)]
    b.graph(S(101), Ee(107), 'nonce：只使用一次的数字', nn, [('cur', 'n2', W(106, '生效'))], '準備一組不同序號，總有一份剛好對上', 'a2', demo='示意')
    b.kw(S(109), Ee(110), '204 秒', '授權生效後 3 分 24 秒，資產開始被批量轉走', icon='clock', danger=True, count=(204, 0, '', ' 秒'))
    b.rows(S(111), Ee(112), '这一笔交易转出', [(W(111, '167'), 'ETH', '167,464 枚', '', 'eth2.png'), (W(111, '16.15'), 'USDT', '约 16.15 亿枚', '', 'usdt.png'), (W(111, '另外'), '其他代币', '几十种', '')],
           (W(112, '25'), '合计约', '$25 亿'), '來源：Blockaid 鏈上分析', 'red')
    b.tiles(S(113), Ee(114), [('私钥被拿走？', 'key', W(114, '私钥')), ('签名服务被利用？', 'pen', W(114, '签名服务'))])
    b.graph(S(115), Ee(117), '印章比喻', [('s', 620, 560, 'stamp', '公司印章', '沒被帶走', W(115, '印章'), False),
                                          ('d', 1300, 560, 'file', '不该盖章的文件', '外面看：印章有效', W(116, '不该盖章'), True)], [('s', 'd', W(116, '盖章的流程'))], aur='a2', demo='示意')
    b.web('bn_sq_invalidate', S(118), Ee(119), logo='binance_mark.png', badge='暫停提現 <em>≠</em> 授權失效', badge_t=S(119))
    b.tiles(S(120), Ee(122), [('正常提现：已暂停', 'pause', W(120, '暂停')), ('链上授权：仍有效', 'alert', W(120, '链上授权')), ('黑客继续转走', 'coins', W(122, '多次'))])
    b.graph(S(123), Ee(126), '为什么清除要花时间', [('p1', 560, 560, 'puzzle', '签名片段 1', '', W(126, '多个部分'), False), ('p2', 960, 560, 'puzzle', '签名片段 2', '', W(126, '多个部分', .2), False),
                                                   ('p3', 1360, 560, 'puzzle', '签名片段 3', '', W(126, '多个部分', .4), False)], [], 'MPC 多方計算：沒有一把單獨的私鑰', 'a2', demo='示意')
    b.web('bn_sq_cleared', S(127), Ee(127), logo='binance_mark.png', badge='10/30 00:10 UTC <em>清除委託代碼</em>', badge_t=S(127, 1.5))

    # ===== money flow / freeze =====
    b.web('elliptic_launder', S(128), Ee(130), logo='elliptic.png', badge='Elliptic：追蹤被盜資金去向', badge_t=S(129))
    b.tiles(S(131), Ee(132), [('USDT · USDC', 'coins', W(131, 'USDT')), ('发行方可冻结', 'snow', W(131, '冻结')), ('同时冻结相关资产', 'shield', W(132, '冻结'))])
    b.kw(S(133), Ee(134), '$0', '已凍結或攔截（凍結 ≠ 已追回）', icon='snow', big=True, count=(28.5, 1, '$', ' 億'))
    b.web('fbi', S(135), Ee(135), logo='fbi.png', badge='FBI：朝鮮黑客組織 <em>TraderTraitor</em>', badge_t=S(135, 2.0))
    b.yt(S(136), Ee(136), [('f24_40', 3.0, 2.4)], 'FRANCE 24')
    b.yt(S(137), Ee(137), [('f24_16', 4.2, 3.6), ('f24_28', .2, 5.8)], 'FRANCE 24 · 幣安公告')
    b.web('bn_sq_users', S(138), Ee(138), logo='binance_mark.png', badge='用戶<em>不承擔</em>損失', badge_t=S(138, .5))
    b.push(S(139), Ee(139), 1.0, 1.08)
    b.yt(S(139), Ee(139), [('f24_8', 2.2, 5.6)], 'FRANCE 24')
    b.web('elliptic_ai', S(140, .8), Ee(142), logo='elliptic.png', badge='Elliptic：沒有 AI 參與的證據', badge_t=S(141, .5))
    b.kw(S(143, .2), Ee(144), '链上数据\n≠ AI 证据', '至於有沒有 AI 自主決策，還無法證明', icon='search')

    # ===== summary =====
    b.tiles(S(145), Ee(146), [('员工设备', 'laptop', W(146, '员工的设备')), ('内部系统', 'server', W(146, '内部的系统')), ('权限管理', 'key', W(146, '权限管理'))])
    b.kw(W(147, 'q day'), Ee(148), 'Q-Day', '量子計算可能威脅現有加密技術', icon='atom')
    b.push(S(149), Ee(150), 1.0, 1.08)
    b.yt(S(149), Ee(149), [('bloomberg_12', .3, 7.5)], 'Bloomberg')
    b.tiles(S(152), Ee(152), [('了解攻击方式', 'search', W(152, '了解')), ('定期检查钱包授权', 'check', W(152, '定期'))])
    b.kw(W(153, '社群'), Ee(153), '加入社群', '下方連結，一起討論', icon='chat')

    # ===== music (funk from the body on; tension only under the teasers + hook) =====
    T, SPLIT, STING, END = ctx['T'], ctx['SPLIT'], ctx['STING'], ctx['BODY_END']
    b.sfx(TEASE + SPLIT, 'hit'); b.sfx(TEASE + SPLIT + .1, 'glow')
    mus = [('mt', 'tension.mp3', 0, TEASE + SPLIT + STING, 0.13)]
    tracks = [('f1.mp3', 203.0), ('f2.mp3', 176.1), ('f3.mp3', 186.6), ('f4.mp3', 153.2), ('f5.mp3', 126.3), ('f6.mp3', 149.0)]
    t = TEASE + SPLIT + STING; k = 0
    while t < END + 5.9 - .5:
        f, d = tracks[k % len(tracks)]; d = min(d - 1.0, END + 5.9 - t)
        mus.append((f'mf{k}', f, t, d, 0.075)); t += d; k += 1
    for id_, f, st, du, vol in mus:
        b.audio.append(f'<audio id="{id_}" src="assets/music2/{f}" data-start="{st:.3f}" data-duration="{du:.3f}" data-media-start="0" data-track-index="{31 + len(b.audio) % 2}" data-volume="{vol}"></audio>')
    return {'under': b.under, 'clips': b.clips, 'css': CSS, 'js': '\n'.join(b.js), 'audio': b.audio, 'cam': b.cam, 'push': b.pushes}
