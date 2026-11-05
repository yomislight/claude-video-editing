"""hf_final/index.html: the whole episode. Times are locked-cut seconds = final seconds."""
import json,os,re,html
A='#5EEAD4'
CUT=421.633;END=3.0;TOTAL=CUT+END
SH=json.load(open('../hf_final/assets/shots/shots.json'))
C=json.load(open('caps.json'))
SKILL=open('../剪辑规范/SKILL.md',encoding='utf8').read().split('---')[-1].strip().split('\n')
c=[];js=[];css=[];N=[0]
E=html.escape
def nid(p='b'):
    N[0]+=1;return f'{p}{N[0]}'
def clip(h,st,en,tr=5):
    c.append(h.replace('§',f'data-start="{st:.3f}" data-duration="{max(en-st,.04):.3f}" data-track-index="{tr}"'))
SX={'click':('1133',.34,.42),'whoosh':('3115',.56,.32),'spark':('3060',1.2,.42),'ping':('3124',.5,.38),'glow':('3083',2.3,.26),'pop':('3005',.18,.4)}
def sfx(t,k):
    f,d,v=SX[k];clip(f'<audio id="{nid("fx")}" src="assets/sfx/{f}.mp3" data-volume="{v}" §></audio>',t,t+d,33+N[0]%3)
PATCH={'后':'後','干':'幹','松':'鬆','准':'準','线':'線'}
def jz(s):
    s=s.replace('后台','后<u>台</u>')
    return re.sub('[后干松准线]',lambda m:f'<u>{PATCH[m.group(0)]}</u>',s)
LG={'claude':'claude.svg','whisper':'openai_word.svg','hf':'hyperframes_app.png','os':'openscreen_app.png','yt':'youtube144.png','ff':'ffmpeg_gh.png','tella':'tella.png','epi':'epidemic.png','nv':'nvidia.svg','heygen':'heygen.png','gh':'github.svg'}
ICON={'scis':'<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M8.5 8L20 19M8.5 16L20 5"/>','cc':'<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M7 12h4M7 15.5h10M14 12h3"/>','star':'<path d="M12 3l2.2 6.3L20.5 12l-6.3 2.7L12 21l-2.2-6.3L3.5 12l6.3-2.7L12 3z"/>','note':'<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>','globe':'<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>','cam':'<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/>','chat':'<path d="M4 5h16v11H9l-5 4V5z"/>','one':'<path d="M6 12l4 4 8-9"/>','like':'<path d="M7 11l4-8c1.5 0 2.5 1 2.5 2.5V9h5.5c1 0 2 1 1.7 2.2l-1.6 7c-.2 1-1 1.8-2.1 1.8H7V11zM3 11h4v9H3z"/>','bell':'<path d="M6 16V11a6 6 0 1112 0v5l2 2H4l2-2zM10 21h4"/>'}
def svg(k): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICON[k]}</svg>'
def lgimg(k,cl=''):
    inv=' inv' if k in('whisper','gh') else ''
    return f'<img class="{cl}{inv}" src="assets/logos/{LG[k]}">'
# ---------- A-roll helpers ----------
SIDE={3.0:'R',7.28:'L',9.46:'R',21.68:'L',24.8:'R',29.52:'L',44.56:'R',65.74:'L',124.02:'R',127.58:'L',140.12:'R',167.18:'L',244.0:'R',297.72:'L',349.36:'R',351.74:'L',386.8:'R',396.26:'L',401.8:'R',416.2:'L'}
def cam(st,en,sd):
    dx=120 if sd=='L' else -120
    js.append(f'tl.fromTo("#aroll",{{x:0,scale:1}},{{x:{dx},scale:1.14,duration:.5,ease:"power3.inOut",immediateRender:false}},{st:.3f});')
    js.append(f'tl.fromTo("#aroll",{{x:{dx},scale:1.14}},{{x:0,scale:1,duration:.32,ease:"power2.inOut",immediateRender:false}},{en-.32:.3f});')
def tiles(st,en,items,by=None,by_t=None,glow=True):
    sd=SIDE[st];i=nid('tl');dx=-60 if sd=='L' else 60
    t=''.join(f'<div class="tile t{k}">{svg(ic) if ic in ICON else lgimg(ic,"tlg")}<span>{jz(w)}</span></div>' for k,(w,ic,_) in enumerate(items))
    b=f'<div class="by">{by}</div>' if by else ''
    clip(f'<div id="{i}" class="clip side s{sd}" §><div class="stack">{t}{b}</div></div>',st,en,5);cam(st,en,sd)
    for k,(_,_,tm) in enumerate(items):
        js.append(f'tl.fromTo("#{i} .t{k}",{{opacity:0,x:{dx},scale:.94}},{{opacity:1,x:0,scale:1,duration:.42,ease:"back.out(1.5)"}},{tm:.3f});');sfx(tm,'click')
    if by:
        js.append(f'tl.to("#{i} .tile",{{borderColor:"{A}",color:"{A}",boxShadow:"0 0 26px rgba(94,234,212,.32)",duration:.35,stagger:.04}},{by_t:.3f});')
        js.append(f'tl.fromTo("#{i} .by",{{opacity:0,y:16}},{{opacity:1,y:0,duration:.45,ease:"power3.out"}},{by_t:.3f});');sfx(by_t,'glow')
def kw(st,en,text,sub=None,logo=None,big=False):
    sd=SIDE[st];i=nid('kw');dx=-60 if sd=='L' else 60;lg=lgimg(logo,'klg') if logo else ''
    s_=f'<small>{sub}</small>' if sub else ''
    clip(f'<div id="{i}" class="clip side s{sd}{" kwb" if big else ""}" §><div class="kin">{lg}<span>{jz(text).replace(chr(10),"<br>")}</span>{s_}</div></div>',st,en,5);cam(st,en,sd)
    js.append(f'tl.fromTo("#{i} .kin",{{opacity:0,x:{dx}}},{{opacity:1,x:0,duration:.55,ease:"power3.out"}},{st+.05:.3f});');sfx(st,'ping')
PUSH=[]
def push(st,en,a=1.0,b=1.08): PUSH.append((st,en,a,b))
# ---------- dark scene ----------
def scene(st,en,body,aur='',snd='whoosh'):
    i=nid('sc');clip(f'<div id="{i}" class="clip scene" §><div class="aur {aur}"></div>{body}</div>',st,en,2)
    if snd: sfx(st,snd)
    return i
ROLES=[('01','剪辑师','Claude Code','claude'),('02','听写员','Whisper','whisper'),('03','动画师','HyperFrames','hf'),('04','资料员','瀏覽器','globe'),('05','录屏','Openscreen','os'),('06','音效师','YouTube 音樂庫','yt'),('07','质检员','FFmpeg','ff')]
def grid(st,en,k=None,allon=None,dim=None):
    h=''
    for n,(no,ro,to,lg) in enumerate(ROLES):
        l=svg('globe') if lg=='globe' else lgimg(lg)
        h+=f'<div class="rc r{n}"><div class="no">{no}</div><div class="ro">{jz(ro)}</div><div class="bx"><div class="lg">{l}</div><span>{to}</span></div></div>'
    i=scene(st,en,f'<div class="grid">{h}</div>')
    js.append(f'tl.fromTo("#{i} .rc",{{opacity:0,y:24}},{{opacity:.5,y:0,duration:.4,stagger:.04,ease:"power3.out"}},{st+.03:.3f});')
    if k is not None:
        js.append(f'tl.to("#{i} .r{k}",{{opacity:1,scale:1.06,borderColor:"{A}",boxShadow:"0 0 60px rgba(94,234,212,.35)",backgroundColor:"rgba(94,234,212,.08)",duration:.45,ease:"power3.out"}},{st+.42:.3f});');sfx(st+.42,'spark')
    if allon:
        for n,t in enumerate(allon):
            js.append(f'tl.to("#{i} .r{n}",{{opacity:1,borderColor:"{A}",duration:.3}},{t:.3f});')
            sfx(allon[n],'click')
    if dim:
        js.append(f'tl.set("#{i} .rc",{{opacity:1,borderColor:"{A}"}},{st+.45:.3f});tl.to("#{i} .rc",{{opacity:.22,borderColor:"rgba(255,255,255,.14)",duration:.8}},{dim:.3f});')
    return i
# ---------- recording with face card ----------
def rec(st,en,src,ms,sw,sh,x0=0.,wf=1.,y0=0.,zoom=None,extra=''):
    WX,WY,WW,WH=600,118,1224,690;TB=44
    W=WW/wf;H=W*sh/sw;L=WX-x0*W;T_=WY+TB-y0
    a=nid('fc');w=nid('win');f=nid('fv');r=nid('rv')
    clip(f'<div id="{a}" class="clip face" §></div>',st,en,3)
    clip(f'<div id="{w}" class="clip win" §><div class="tb"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i><span>{extra}</span></div></div>',st,en,3)
    clip(f'<video id="{f}" class="clip fv" src="assets/aroll.mp4" muted playsinline data-media-start="{st:.3f}" §></video>',st,en,4)
    R,B=W-x0*W-WW,H-y0-(WH-TB)
    clip(f'<video id="{r}" class="clip rv" src="assets/{src}" muted playsinline data-media-start="{ms:.3f}" style="left:{L:.1f}px;top:{T_:.1f}px;width:{W:.1f}px;height:{H:.1f}px;clip-path:inset({y0:.1f}px {R:.1f}px {B:.1f}px {x0*W:.1f}px round 0 0 18px 18px)" §></video>',st,en,4)
    js.append(f'tl.fromTo("#{w},#{r}",{{opacity:0,x:50}},{{opacity:1,x:0,duration:.5,ease:"power3.out"}},{st+.03:.3f});')
    js.append(f'tl.fromTo("#{a},#{f}",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.5,ease:"power3.out"}},{st+.03:.3f});')
    sfx(st,'whoosh')
    if zoom:
        ox,oy=WX+WW/2-L,WY+WH/2-T_
        js.append(f'tl.set("#{r}",{{transformOrigin:"{ox:.0f}px {oy:.0f}px"}},{st:.3f});tl.to("#{r}",{{scale:1.28,duration:.7,ease:"power3.inOut"}},{zoom:.3f});');sfx(zoom,'ping')
    bg=nid('sb');clip(f'<div id="{bg}" class="clip scene" §><div class="aur a2"></div></div>',st,en,2)
# ---------- 3D page ----------
def web(st,en,shot,crop=(0,0,1440),rects=None,logo=None,badge=None,badge_t=None,dom=None,hl_t=None,ih=900):
    m=SH.get(shot,{'url':'https://claude.com/pricing'});cx,cy,cw=crop;s=1260/cw
    rs=rects if rects is not None else (m.get('rects') or [])
    hl=''.join(f'<div class="hl" style="left:{r["x"]*s-cx*s-6:.0f}px;top:{r["y"]*s-cy*s-4:.0f}px;width:{r["w"]*s+12:.0f}px;height:{r["h"]*s+8:.0f}px"></div>' for r in rs[:2])
    d=dom or m['url'].split('/')[2]
    lg=f'<div class="wlg{" wh" if logo in ("nv","tella") else ""}">{lgimg(logo)}</div>' if logo else ''
    bd=f'<div class="wbd"><span>{badge}</span></div>' if badge else ''
    i=scene(st,en,f'<div class="persp"><div class="bw"><div class="tb"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i><span>{d}</span></div><div class="wv2"><img src="assets/shots/{shot}.png" style="left:{-cx*s:.0f}px;top:{-cy*s:.0f}px;width:{1440*s:.0f}px;height:{ih*s:.0f}px">{hl}</div></div>{lg}{bd}</div>','a3')
    js.append(f'tl.fromTo("#{i} .bw",{{rotateY:-20,rotateX:9,y:60,opacity:0,scale:.9}},{{rotateY:-6,rotateX:3,y:0,opacity:1,scale:1,duration:.8,ease:"power3.out"}},{st+.03:.3f});')
    js.append(f'tl.to("#{i} .bw",{{rotateY:0,rotateX:0,scale:1.06,duration:{max(en-st-.85,.5):.2f},ease:"power1.inOut"}},{st+.82:.3f});')
    if logo: js.append(f'tl.fromTo("#{i} .wlg",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.45,ease:"back.out(1.8)"}},{st+.45:.3f});')
    if hl:
        t=hl_t or min(st+1.0,en-.8);js.append(f'tl.fromTo("#{i} .hl",{{scaleX:0}},{{scaleX:1,duration:.5,stagger:.2,ease:"power2.out"}},{t:.3f});');sfx(t,'ping')
    if badge:
        t=badge_t or st+1.4;js.append(f'tl.fromTo("#{i} .wbd",{{opacity:0,y:18}},{{opacity:1,y:0,duration:.4,ease:"back.out(1.6)"}},{t:.3f});');sfx(t,'pop')
    return i
def ccrop(shot,x,y,w,h,W):
    s=W/w;return f'<div class="cc" style="width:{W}px;height:{h*s:.0f}px"><img src="assets/shots/{shot}.png" style="left:{-x*s:.0f}px;top:{-y*s:.0f}px;width:{1440*s:.0f}px;height:{900*s:.0f}px"></div>'
def fade(i,sel,t,y=26,dur=.45,ease='power3.out'):
    js.append(f'tl.fromTo("#{i} {sel}",{{opacity:0,y:{y}}},{{opacity:1,y:0,duration:{dur},ease:"{ease}"}},{t:.3f});')
# ========================= CUES =========================
# ----- Hook
tiles(3.0,7.28,[('剪辑','scis',3.25),('字幕','cc',3.75),('动画','star',4.2),('配乐','note',4.7)],f'<img src="assets/logos/claude.svg"><span>全部由 Claude 完成</span>',5.5)
kw(7.28,9.36,'时间线\n0 次','我一下都沒有碰過')
kw(9.46,16.2,'$0','除了 Claude 會員，其餘工具全部免費',big=True)
web(16.4,21.68,'yt_search',(0,0,1440),rects=[],dom='youtube.com',logo='yt')
kw(21.68,24.8,'按月付费','很多教程裡，好幾個工具都要訂閱')
kw(24.8,29.52,'全免费\n中文版',big=True)
tiles(29.52,35.96,[('哪几个工具','one',29.65),('怎么教风格','one',31.0),('花多少钱','one',32.7)])
push(35.96,41.02)
push(41.02,44.56,1.08,1.0)
tiles(44.56,49.2,[('开机录','cam',46.74),('给意见','chat',47.7)])
grid(49.2,55.2,allon=[49.6+.55*n for n in range(7)])
# ----- 1
grid(55.2,56.66,0)
lane=''.join(f'<div class="cl c{n}"></div>' for n in range(12))
i=scene(56.66,65.74,f'<div class="pt">坐在時間線前面好幾個小時</div><div class="laneb"><div class="lanelb">時間線</div><div class="lane">{lane}</div><div class="ph1"><span class="tg g1">挑能用的</span><span class="tg g2">刪掉講錯的</span><span class="tg g3">哪裡放大</span><span class="tg g4">哪裡加動畫</span></div></div>')
js.append(f'tl.fromTo("#{i} .cl",{{opacity:0,scaleY:.3}},{{opacity:1,scaleY:1,duration:.3,stagger:.05}},{56.9:.3f});')
for t,g in ((60.8,'g1'),(61.7,'g2'),(62.82,'g3'),(64.46,'g4')): fade(i,'.'+g,t);sfx(t,'click')
js.append(f'tl.to("#{i} .c1,#{i} .c4,#{i} .c5,#{i} .c8,#{i} .c10",{{backgroundColor:"#3a3f4c",duration:.3}},60.8);')
js.append(f'tl.to("#{i} .c4,#{i} .c8",{{backgroundColor:"#ff5f57",duration:.25}},61.7);tl.to("#{i} .c4,#{i} .c8",{{opacity:.15,duration:.3}},62.2);')
js.append(f'tl.to("#{i} .c6",{{backgroundColor:"{A}",scaleY:1.5,duration:.3}},62.82);tl.to("#{i} .c9",{{backgroundColor:"#818cf8",scaleY:1.3,duration:.3}},64.46);')
kw(65.74,71.64,'专案经理','Claude Code 就是整支影片的總指揮','claude')
rec(71.64,83.74,'r1.mov',14,2940,1848,.21,.575,70,extra='Claude Code')
# ----- 2
push(83.74,90.04)
grid(90.04,92.68,1)
SRT=[('00:00:16','哈囉大家好'),('00:00:18','這兩天幣圈最大的消息'),('00:00:21','就是幣安遭遇了黑客襲擊'),('00:00:24','涉及資產大約 63 億美元')]
bars=''.join(f'<i style="height:{20+abs((n*37)%70)}px"></i>' for n in range(46))
rows=''.join(f'<div class="ln l{n}"><b>{a}</b><span>{b}</span></div>' for n,(a,b) in enumerate(SRT))
i=scene(92.68,96.58,f'<div class="wave">{bars}</div><div class="arrow">↓</div><div class="tx">{rows}</div>')
js.append(f'tl.fromTo("#{i} .wave i",{{scaleY:.1,opacity:.2}},{{scaleY:1,opacity:1,duration:.4,stagger:.012}},92.8);')
for n in range(4): fade(i,f'.l{n}',93.3+n*.55,14);sfx(93.3+n*.55,'click')
web(96.58,101.72,'parakeet',(60,70,960),logo='nv',dom='huggingface.co/nvidia',badge='支援語言：English，<em>不支援中文</em>',badge_t=99.2)
web(101.72,110.72,'whisper',(800,180,640),logo='whisper',dom='github.com/openai/whisper',hl_t=103.2,badge='開源　·　本機執行　·　完全免費',badge_t=107.2)
srtf=open(os.environ.get('SAMPLE_SRT','sample.srt'),encoding='utf8',errors='ignore').read().split('\n')[:14]
rows=''.join(f'<div class="sl">{E(x) or "&nbsp;"}</div>' for x in srtf)
i=scene(110.72,115.82,f'<div class="pt">也可以直接導出剪映字幕</div><div class="edit"><div class="tb"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i><span>11月4日字幕.srt</span></div><div class="sb">{rows}</div></div>')
fade(i,'.edit',110.9)
takes=lambda: '<div class="scr">腳本：我是導演，Claude 是我的剪輯師</div><div class="tks"><div class="tk k0"><b>第 1 遍</b><i></i><span>講錯了</span></div><div class="tk k1"><b>第 2 遍</b><i></i><span>卡住了</span></div><div class="tk k2"><b>第 3 遍</b><i></i><span>最後一條，講完整</span></div></div>'
def takesc(st,en):
    i=scene(st,en,takes());fade(i,'.scr',st+.05)
    for n in range(3): fade(i,f'.k{n}',st+.5+n*.45,16)
    js.append(f'tl.to("#{i} .k2",{{borderColor:"{A}",boxShadow:"0 0 50px rgba(94,234,212,.3)",duration:.4}},{min(st+2.4,en-.8):.3f});');sfx(min(st+2.4,en-.8),'spark')
takesc(115.82,121.9)
# ----- 3
grid(121.9,124.02,2)
tiles(124.02,127.58,[('片头标题','star',124.1),('弹出 logo','star',125.2),('数字跳动','star',126.0)])
kw(127.58,129.42,'After Effects','以前要專門打開')
web(129.42,133.2,'hyperframes_top',(690,170,750),rects=[{'x':1056,'y':300,'w':225,'h':18},{'x':1056,'y':324,'w':110,'h':18}],hl_t=130.3,logo='hf',dom='github.com/heygen-com/hyperframes',badge='HeyGen 開源　·　免費',badge_t=131.0)
code=E('<h1 class="title">一支影片</h1>\ngsap.to(".title", { y: 0, opacity: 1 })')
i=scene(133.2,140.12,f'<div class="flow"><div class="fn n0"><h5>1　程式碼</h5><pre>{code}</pre></div><div class="fa a0">→</div><div class="fn n1"><h5>2　小網頁</h5><div class="mini"><span>一支影片</span></div></div><div class="fa a1">→</div><div class="fn n2"><h5>3　影片</h5><div class="mini mp"><em>▶</em></div></div></div>')
for t,s in ((134.7,'.n0'),(136.4,'.a0'),(136.5,'.n1'),(137.5,'.a1'),(137.7,'.n2')): fade(i,s,t,18);
for t in (134.7,136.5,137.7): sfx(t,'click')
kw(140.12,143.3,'本机执行\n$0','全部在自己的電腦上跑')
rec(143.3,148.12,'r7.mp4',1,1920,1080,0,1,10,extra='HyperFrames Studio')
# ----- 4
grid(148.12,149.5,3)
push(149.5,154.5)
i=scene(154.5,160.52,f'<div class="pt">畫面上直接放出證據</div><div class="ev"><div class="evc e0"><h5>官方公告</h5>{ccrop("bn_notice1",310,110,700,500,560)}</div><div class="evc e1"><h5>推文</h5>{ccrop("x_anthropic",96,300,600,460,560)}</div><div class="evc e2"><h5>新聞</h5>{ccrop("coindesk_ai",290,590,680,300,560)}</div></div>')
for n,t in enumerate((157.3,158.1,158.9)): fade(i,f'.e{n}',t);sfx(t,'click')
web(160.52,167.18,'bn_sq_multistage',(0,74,1037),dom='binance.com',hl_t=164.9)
kw(167.18,172.96,'只用\n真实截图','不准自己編推文、編新聞')
# ----- 5
grid(172.96,174.86,4)
web(174.86,181.88,'openscreen',(700,240,740),logo='os',dom='github.com/siddharthvaddem/openscreen',hl_t=178.6)
i=scene(181.88,186.14,f'<div class="pt">同時錄螢幕和攝影機，分成兩個檔案</div><div class="r9c"><img src="assets/r9.jpg"></div><div class="fl"><div class="ff f0">recording-1775708613446.webm<small>螢幕</small></div><div class="ff f1">recording-1775708613446-webcam.webm<small>攝影機</small></div></div>')
fade(i,'.r9c',182.0);fade(i,'.f0',184.0,14);fade(i,'.f1',184.5,14);sfx(184,'click');sfx(184.5,'click')
rec(186.14,194.68,'r1.mov',20,2940,1848,.21,.575,70,zoom=190.6,extra='Claude Code')
# ----- 6
grid(194.68,196.1,5)
marks=''.join(f'<span class="mk m{n}" style="left:{x}%"></span>' for n,x in enumerate((12,28,47,63,81)))
i=scene(196.1,200.62,f'<div class="pt">哪一段配什麼音樂，什麼時候加音效</div><div class="tr"><label>音樂</label><div class="tb1"><div class="m1b"></div><div class="m2b"></div></div></div><div class="tr"><label>音效</label><div class="tb2">{marks}</div></div>')
js.append(f'tl.fromTo("#{i} .m1b",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"power2.out"}},196.5);tl.fromTo("#{i} .m2b",{{scaleX:0}},{{scaleX:1,duration:.7,ease:"power2.out"}},197.0);')
for n in range(5): js.append(f'tl.fromTo("#{i} .m{n}",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2.2)"}},{198.9+n*.28:.3f});')
web(200.62,205.3,'epidemic_pricing',(40,120,1360),logo='epi',dom='epidemicsound.com/pricing',badge='按月付費',badge_t=202.9)
i=scene(205.3,212.52,f'<div class="yt">{lgimg("yt")}<span>YouTube 音樂庫　·　免費　·　版權安全</span></div><div class="r8"><img class="r0" src="assets/r8_1.jpg"><img class="r1" src="assets/r8_2.jpg"><img class="r2" src="assets/r8_3.jpg"></div>')
fade(i,'.yt',205.4,16)
for n,t in enumerate((205.6,207.6,209.4)): fade(i,f'.r{n}',t,30);sfx(t,'click')
i=scene(212.52,222.02,f'<svg class="vc" viewBox="0 0 1500 420" fill="none"><path class="vp" d="M20 110 C 300 110,430 110,560 200 S 900 300,1480 300" stroke="{A}" stroke-width="7" stroke-linecap="round"/></svg><div class="vl v0" style="left:300px;top:270px">開頭：懸疑</div><div class="vl v1" style="left:900px;top:420px">正文：輕鬆</div><div class="vl v2" style="left:1400px;top:450px">音量壓低</div><div class="vbase"><span>大</span><span>音量</span><span>小</span></div>')
js.append(f'tl.fromTo("#{i} .vc",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:6.5,ease:"none"}},213.6);')
for t,s in ((214.1,'.v0'),(216.3,'.v1'),(219.0,'.v2')): fade(i,s,t,18);sfx(t,'click')
# ----- 7
grid(222.02,223.66,6)
TERM=['$ ffmpeg -i 粗剪.mp4 -vf blackdetect -af ebur128 -f null -','frame=12649  fps=30  time=00:07:01.63','black_detect: 0 段黑屏','Integrated loudness:  I: -21.3 LUFS','Loudness range:     LRA: 4.8 LU','質檢通過：畫面和聲音長度一致']
rows=''.join(f'<div class="tl t{n}">{E(x)}</div>' for n,x in enumerate(TERM))
i=scene(223.66,228.76,f'<div class="edit term"><div class="tb"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i><span>Terminal</span></div><div class="sb">{rows}</div></div>')
fade(i,'.edit',223.75)
for n in range(6): js.append(f'tl.fromTo("#{i} .t{n}",{{opacity:0}},{{opacity:1,duration:.1}},{224.1+n*.6:.3f});')
web(228.76,233.98,'ffmpeg',(150,110,1200),logo='ff',dom='ffmpeg.org',hl_t=230.0,badge='二十多年的免費開源工具',badge_t=231.2)
push(233.98,237.4)
# ----- rules
grid(237.4,244.0,dim=240.5)
kw(244.0,251.58,'剪辑规范\nSkill','最關鍵的東西',big=True)
lines=''.join(f'<div class="sl {"h" if x.startswith("#") else ""}">{E(x) or "&nbsp;"}</div>' for x in SKILL)
i=scene(251.58,263.46,f'<div class="edit skl"><div class="tb"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i><span>剪辑规范/SKILL.md</span></div><div class="sb"><div class="scroll">{lines}</div></div></div><div class="chk"><div class="ci q0">字幕什麼顏色</div><div class="ci q1">logo 放哪裡</div><div class="ci q2">句子留多少空隙</div><div class="ci q3">音樂開多大</div></div>')
fade(i,'.edit',251.7)
js.append(f'tl.to("#{i} .scroll",{{y:-300,duration:11,ease:"none"}},252.3);')
for n,t in enumerate((256.56,258.2,259.88,261.66)): fade(i,f'.q{n}',t,14);sfx(t,'click')
rec(263.46,269.68,'r11.mov',3,2940,1848,.21,.575,650,extra='Claude Code')
RU=['同一句話錄了好幾遍，用最後一條講完整的','句子和句子之間，留 0.2 秒','提詞的口令、講錯的，全部刪掉','粗剪先不動畫面，只管把話剪順']
rows=''.join(f'<div class="ru u{n}"><b>{n+1}</b><span>{x}</span></div>' for n,x in enumerate(RU))
i=scene(269.68,283.42,f'<div class="pt">我念幾條給大家聽</div><div class="rl">{rows}</div>')
for n,t in enumerate((270.96,275.02,277.48,279.82)): fade(i,f'.u{n}',t);sfx(t,'click')
# ----- teach
push(283.42,290.76)
rec(290.76,297.72,'r11.mov',9,2940,1848,.21,.575,650,extra='Claude Code')
i=nid('nb');clip(f'<div id="{i}" class="clip notes" §><div class="nt nq0"><b>00:22</b>字幕太大了</div><div class="nt nq1"><b>這一句</b>該刪掉</div></div>',290.76,297.72,6)
fade(i,'.nq0',293.62);fade(i,'.nq1',296.3);sfx(293.62,'pop');sfx(296.3,'pop')
kw(297.72,304.76,'记进\n剪辑规范','把你剛剛學到的東西',big=True)
push(304.76,310.36,1.08,1.0)
# ----- demo
push(310.36,313.3)
i=scene(313.3,319.9,'<div class="pt">原始素材</div><div class="bar43"><div class="b43"><span>43:34</span></div><i class="x0" style="left:9%">重錄</i><i class="x1" style="left:33%">口誤</i><i class="x2" style="left:58%">停頓</i><i class="x3" style="left:79%">重錄</i></div>')
js.append(f'tl.fromTo("#{i} .b43",{{scaleX:0}},{{scaleX:1,duration:.7,ease:"power3.out"}},313.5);')
for n in range(4): fade(i,f'.x{n}',317.4+n*.42,12);sfx(317.4+n*.42,'click')
rec(319.9,324.16,'r4.mov',23.8,2940,1848,.2,.8,315,extra='Claude Code')
takesc(324.16,329.66)
i=scene(329.66,334.22,'<div class="cnt"><div class="cn1">43:34<em>→</em><b>16:14</b></div><div class="cn2"><span class="num">0</span> 刀</div></div>')
fade(i,'.cn1',329.8)
js.append(f'(function(){{const o={{v:0}};const el=document.querySelector("#{i} .num");tl.to(o,{{v:369,duration:1.7,ease:"power2.out",onUpdate:()=>{{el.textContent=Math.round(o.v)}}}},332.1);}})();');sfx(332.1,'ping')
i=scene(334.22,337.92,'<div class="pt">順手導出工程檔</div><div class="fl fl2"><div class="ff f0">幣安被盜_粗剪_Premiere.xml<small>Premiere Pro</small></div><div class="ff f1">幣安被盜_粗剪.fcpxml<small>Final Cut Pro</small></div></div>')
fade(i,'.f0',335.0,14);fade(i,'.f1',335.8,14);sfx(335,'click');sfx(335.8,'click')
rec(337.92,341.26,'r6.mov',8,2940,1848,0,.87,110,extra='時間線')
push(341.26,349.36,1.08,1.0)
kw(349.36,351.74,'我是导演','Claude 是我的剪輯師')
# ----- cost
kw(351.74,354.92,'成本',big=True)
web(354.92,358.38,'claude_pricing_hi',(20,400,1300),ih=1100,rects=[{'x':607,'y':731,'w':38,'h':17},{'x':430,'y':748,'w':88,'h':17}],logo='claude',dom='claude.com/pricing',hl_t=356.6,badge='Pro 月付 $22',badge_t=357.0)
push(358.38,363.48)
PR=[('claude.svg','Claude Ultra 頂配','ultra','claude.com/pricing',363.9),('tella.png','錄屏 Tella','tella','tella.com/pricing',367.3),('epidemic.png','音樂 Epidemic Sound','epidemic','epidemicsound.com/pricing',368.3)]
rr=''.join(f'<div class="pc p{k}"><div class="ph"><img class="plg{" e" if lg.startswith("epi") else ""}" src="assets/logos/{lg}"><span>{n}</span></div><div class="pv"><img src="assets/crops/{cr}.png"></div><div class="ps">{sr}</div></div>' for k,(lg,n,cr,sr,_) in enumerate(PR))
i=scene(363.48,371.82,f'<div class="plist">{rr}</div><div class="sum"><span>三個訂閱，每月合計約</span><b>$243</b></div><div class="pc mine"><div class="ph"><img class="plg" src="assets/logos/claude.svg"><span>我用的 Claude Pro</span></div><div class="pv"><img src="assets/crops/pro.png"><i style="left:67.5%;top:76.5%;width:12.5%;height:8.6%"></i><i style="left:8.2%;top:85%;width:29.5%;height:8.6%"></i></div><div class="big"><b>$22</b><span>／月（月付）</span></div><div class="ps">其餘工具全部免費</div></div>','a2')
for k,(*_,t) in enumerate(PR): fade(i,f'.p{k}',t,34,.5);sfx(t,'click')
fade(i,'.sum',369.0,16,.4)
js.append(f'tl.to("#{i} .plist",{{scale:.66,y:-8,opacity:.45,duration:.6,ease:"power3.inOut"}},369.65);tl.to("#{i} .sum",{{y:-130,scale:.8,opacity:.6,duration:.6,ease:"power3.inOut"}},369.65);')
js.append(f'tl.fromTo("#{i} .mine",{{opacity:0,x:70,scale:.94}},{{opacity:1,x:0,scale:1,duration:.6,ease:"power3.out"}},369.75);');sfx(369.75,'glow')
i=scene(371.82,377.72,'<div class="usg"><div class="ug1">剪完一支 40 多分鐘素材的粗剪</div><div class="ug2"><div class="ugb"></div></div><div class="ug3"><span>本週額度</span><b>约 1/3</b></div></div>')
fade(i,'.ug1',372.0)
js.append(f'tl.fromTo("#{i} .ugb",{{scaleX:0}},{{scaleX:1,duration:1.2,ease:"power2.out"}},374.9);');fade(i,'.ug3',375.4,14);sfx(374.9,'ping')
TW=[('whisper','Whisper',377.8),('hf','HyperFrames',378.5),('ff','FFmpeg',379.2),('os','Openscreen',382.1),('yt','YouTube 音樂庫',383.8)]
rows=''.join(f'<div class="wc w{n}"><div class="lg">{lgimg(k)}</div><span>{x}</span><em>免費</em></div>' for n,(k,x,_) in enumerate(TW))
i=scene(377.72,386.8,f'<div class="wall">{rows}</div>')
for n,(*_,t) in enumerate(TW): fade(i,f'.w{n}',t,26);sfx(t,'click')
kw(386.8,390.14,'额外花费\n$0',big=True)
push(390.14,396.26)
tiles(396.26,401.8,[('当天拍','one',396.5),('当天剪','one',397.2),('当天发','one',397.9)])
# ----- end
kw(401.8,409.26,'剪辑规范\nSkill','免費分享，連結放在影片下方說明欄','gh')
push(409.26,416.2)
tiles(416.2,419.12,[('点赞','like',416.5),('订阅','bell',417.1)])
i=nid('endc');clip(f'<div id="{i}" class="clip scene" §><div class="aur"></div><div class="endt"><span>{jz("感谢观看")}</span><small>Yomi</small></div></div>',CUT,TOTAL,2)
fade(i,'.endt',CUT+.1)
# ---------- A-roll, scrim, captions, audio ----------
clip(f'<video id="aroll" class="clip full" src="assets/aroll.mp4" muted playsinline data-media-start="0" §></video>',0,CUT,0)
clip('<div id="scrim" class="clip scrim" §></div>',0,CUT,1)
for st,en,a,b in PUSH:
    js.append(f'tl.fromTo("#aroll",{{scale:{a}}},{{scale:{b},duration:{en-st:.2f},ease:"none",immediateRender:false}},{st:.3f});tl.set("#aroll",{{scale:1}},{en:.3f});')
acc=sorted(C['acc'],key=len,reverse=True);rx=re.compile('|'.join(map(re.escape,acc)))
for k,x in enumerate(C['caps']):
    s=x['t'];s=rx.sub(lambda m:f'\x01{m.group(0)}\x02',s,count=1);s=jz(E(s)).replace('\x01','<b>').replace('\x02','</b>')
    clip(f'<div id="cap{k}" class="clip cap" §><span>{s}</span></div>',x['s'],x['e'],20)
clip('<audio id="voice" src="assets/voice.m4a" data-volume="1" data-media-start="0" §></audio>',0,CUT,30)
clip('<audio id="mh" src="assets/music/hook.mp3" data-volume="0.08" data-media-start="0" §></audio>',0,41.02,31)
clip('<audio id="mb1" src="assets/music/body1.mp3" data-volume="0.08" data-media-start="0" §></audio>',41.02,41.02+176.1,31)
clip('<audio id="mb2" src="assets/music/body2.mp3" data-volume="0.08" data-media-start="0" §></audio>',217.12,217.12+186.6,31)
clip('<audio id="mb3" src="assets/music/body3.mp3" data-volume="0.09" data-media-start="0" §></audio>',403.72,TOTAL,31)
sfx(41.02,'whoosh')
CSS=open('final.css',encoding='utf8').read().replace('$A',A)
page=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/><title>Claude 剪輯教程 成片</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="{TOTAL:.3f}">
{chr(10).join(c)}
</div><script>const tl=gsap.timeline({{paused:true}});
{chr(10).join(js)}
window.__timelines["main"]=tl;</script></body></html>'''
open('../hf_final/index.html','w',encoding='utf8').write(page)
print('total',TOTAL,'clips',len(c))
