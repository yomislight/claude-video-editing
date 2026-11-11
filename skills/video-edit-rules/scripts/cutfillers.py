"""Remaining fillers: locate precisely in the CUT (short windows), map the cut interval back to source pieces (may span a cut)."""
import json,subprocess,sys
from funasr import AutoModel
m=AutoModel(model="paraformer-zh",vad_model="fsmn-vad",disable_update=True,disable_pbar=True)
S=json.load(open('segments.json'));fps=S['fps'];segs=S['segments']
drops=json.load(open('drops.json'));k=0
def c2src(cs,ce):
    out=[];off=0
    for a,b,_ in segs:
        s0,e0=off/fps,(off+b-a)/fps
        lo,hi=max(cs,s0),min(ce,e0)
        if hi>lo: out.append((a/fps+lo-s0,a/fps+hi-s0))
        off+=b-a
    return out
for line in open(sys.argv[1],encoding='utf8'):
    s,e,ch,ctx=line.rstrip('\n').split('\t')
    if '总【额】' in ctx: continue
    s=float(s);a0=max(0,s-2)
    subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{a0:.2f}','-to',f'{s+2:.2f}','-i','cut16k.wav','probe/cw.wav'],check=True)
    r=m.generate(input='probe/cw.wav')[0];tk=r['text'].split();tt=r['timestamp']
    c=[(abs(a0+tt[j][0]/1000-s),a0+tt[j][0]/1000,a0+tt[j][1]/1000) for j,t in enumerate(tk) if t==ch]
    if not c: print('NOT FOUND',ctx);continue
    _,cs,ce=min(c)
    for p,q in c2src(cs-0.02,ce+0.03):
        drops.append([round(p,2),round(q,2),'R2-10 语气词(刀口) '+ctx]);k+=1
    print(f'{cs:.2f}-{ce:.2f}',c2src(cs-0.02,ce+0.03),ctx)
json.dump(drops,open('drops.json','w'),ensure_ascii=False,indent=1);print(k)
