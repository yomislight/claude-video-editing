"""Turn chosen repeat hits (cut-time ranges from repeats.py) into source-time drops, snapped to energy dips."""
import json,sys,wave,numpy as np
segs=json.load(open('segments.json'));fps=segs['fps'];S=segs['segments']
d=json.load(open(sys.argv[1]));tok=d['text'].split();ts=d['ts']
w=wave.open('audio16k.wav');sr=w.getframerate()
x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
hop=160;n=len(x)//hop;db=20*np.log10(np.sqrt(np.mean(x[:n*hop].reshape(n,hop)**2,axis=1))+1e-10)
db=np.convolve(db,np.ones(3)/3,mode='same')
def c2s(t):  # cut seconds -> source seconds
    off=0
    for a,b,_ in S:
        if off/fps<=t<(off+b-a)/fps: return a/fps+(t-off/fps)
        off+=b-a
    return None
def dip(t,win=0.15):
    f=np.arange(int((t-win)*100),int((t+win)*100));return f[np.argmin(db[f]+np.abs(f-t*100)*0.05)]/100
def tsec(ms): return ms/1000
targets=[l.strip() for l in open(sys.argv[2]) if l.strip() and not l.startswith('#')]
drops=json.load(open('drops.json'))
for tg in targets:
    a,b=tg.split()[0].split('–')
    def p(s): m,s=s.split(':');return int(m)*60+float(s)
    ca,cb=p(a),p(b)
    sa,sb=c2s(ca),c2s(cb)
    if sa is None or sb is None or sb<sa or sb-sa>8: print('SKIP (crosses cut)',tg);continue
    da,db_=dip(sa-0.04),dip(sb-0.04)
    drops.append([round(da,2),round(db_,2),'repeat '+tg.split(None,1)[1]])
    print(f'{tg}\t-> src {da:.2f}-{db_:.2f}')
json.dump(drops,open('drops.json','w'),ensure_ascii=False,indent=1)
