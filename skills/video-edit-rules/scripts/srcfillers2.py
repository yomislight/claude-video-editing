"""Precise filler drops: candidates from long-file FunASR, then re-located in a short source window (±2 s)."""
import json,subprocess,wave,numpy as np
from funasr import AutoModel
F=set('嗯呃额啊呀哎诶唉哦喔噢欸哇')
m=AutoModel(model="paraformer-zh",vad_model="fsmn-vad",disable_update=True,disable_pbar=True)
drops=[x for x in json.load(open('drops.json')) if '语气词' not in x[2]]
S=json.load(open('segments.json'));fps=S['fps'];segs=[(a/fps,b/fps) for a,b,_ in S['segments']]
d=json.load(open('src_fasr.json'));tok=d['text'].split();ts=d['ts']
w=wave.open('audio16k.wav');x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
hop=160;n=len(x)//hop;db=20*np.log10(np.sqrt(np.mean(x[:n*hop].reshape(n,hop)**2,axis=1))+1e-10)
def dip(t,lo,hi):
    f=np.arange(int((t+lo)*100),int((t+hi)*100));return f[np.argmin(db[f])]/100
cands=[]
for i,t in enumerate(tok):
    if t not in F or (t=='额' and tok[i-1]=='总'): continue
    s,e=ts[i][0]/1000,ts[i][1]/1000
    if sum(max(0,min(e+0.3,b)-max(s-0.3,a)) for a,b in segs)<0.1: continue
    cands.append((s,e,tok[i-1] if i else '',t))
done=set();k=0
for s,e,prev,t in cands:
    a0=max(0,s-2.0);b0=s+2.0
    subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{a0:.2f}','-to',f'{b0:.2f}','-i','audio16k.wav','probe/fw.wav'],check=True)
    r=m.generate(input='probe/fw.wav')[0];tk=r['text'].split();tt=r['timestamp']
    best=None
    for j,c in enumerate(tk):
        if c==t:
            cs=a0+tt[j][0]/1000;ce=a0+tt[j][1]/1000
            score=abs(cs-s)-(0.3 if j and tk[j-1]==prev else 0)
            if best is None or score<best[0]: best=(score,cs,ce,j)
    if not best or abs(best[1]-s)>0.6: print('NOT FOUND',f'{s:.2f}',prev+t);continue
    _,cs,ce,j=best
    if round(cs,1) in done: continue
    done.add(round(cs,1))
    if sum(max(0,min(ce,b)-max(cs,a)) for a,b in segs)<0.4*(ce-cs): continue
    a=dip(cs,-0.05,0.03);b=dip(ce,-0.03,0.08)
    ctx=''.join(tk[max(0,j-5):j])+'【'+t+'】'+''.join(tk[j+1:j+5])
    drops.append([round(a,2),round(b,2),'R2-10 语气词 '+ctx]);k+=1
    print(f'{cs:8.2f}-{ce:.2f} -> {a:.2f}-{b:.2f}  {ctx}')
json.dump(drops,open('drops.json','w'),ensure_ascii=False,indent=1);print(k,'filler drops')
