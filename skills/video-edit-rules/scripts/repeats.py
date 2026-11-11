"""Find restarts/repeats in a verbatim FunASR transcript: same >=2-token run appearing again within a few tokens."""
import json,sys
d=json.load(open(sys.argv[1]));tok=d['text'].split();ts=d['ts']
assert len(tok)==len(ts),(len(tok),len(ts))
def mmss(ms): s=ms/1000;return f"{int(s//60):02d}:{s%60:05.2f}"
hits=[];i=0
while i<len(tok):
    best=None
    for n in range(8,1,-1):
        a=tok[i:i+n]
        for gap in range(0,4):
            j=i+n+gap
            if tok[j:j+n]==a: best=(n,gap,j);break
        if best:break
    if best:
        n,gap,j=best
        ctx=''.join(tok[max(0,i-6):j+n+4])
        hits.append((ts[i][0],ts[j][0],''.join(tok[i:j]),ctx))
        i=j
    else: i+=1
for a,b,rep,ctx in hits: print(f"{mmss(a)}–{mmss(b)}\t删「{rep}」\t…{ctx}…")
print(len(hits),'hits',file=sys.stderr)
