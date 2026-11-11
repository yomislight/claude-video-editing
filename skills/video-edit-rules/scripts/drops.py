"""Post-process segments.json after build_edl.py.
fills.json: [[start,end,note]] source ranges that must be kept whole (extends/merges neighbouring segments within 1 s).
drops.json: [[start,end,note]] source ranges to remove (applied after fills, so drops win).
The untouched list is saved to segments_raw.json."""
import json,os
d=json.load(open('segments.json'));fps=d['fps']
json.dump(d,open('segments_raw.json','w'))
S=[list(s) for s in d['segments']]
fills=json.load(open('fills.json')) if os.path.exists('fills.json') else []
for a,b,*_ in fills:
    fa,fb=round(a*fps),round(b*fps)
    near=[i for i,(p,q,l) in enumerate(S) if q>=fa-fps and p<=fb+fps]
    if not near: print('fill not near any segment',a,b);continue
    i,j=near[0],near[-1]
    S[i]=[min(S[i][0],fa),max(S[j][1],fb),S[i][2]]
    del S[i+1:j+1]
drops=[(round(a*fps),round(b*fps)) for a,b,*_ in json.load(open('drops.json'))]
out=[]
for a,b,l in S:
    parts=[[a,b]]
    for s,e in drops:
        nxt=[]
        for p,q in parts:
            if e<=p or s>=q: nxt.append([p,q]);continue
            if s>p: nxt.append([p,s])
            if e<q: nxt.append([e,q])
        parts=nxt
    out+=[[p,q,l] for p,q in parts if q-p>=3]
d['segments']=out;json.dump(d,open('segments.json','w'))
print(len(out),'segments',round(sum(q-p for p,q,_ in out)/fps,2),'s')
