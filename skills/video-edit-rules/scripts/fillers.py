"""List filler particles in a verbatim FunASR transcript with cut times and context."""
import json,sys
F=set('嗯呃额啊呀哎诶唉哦喔噢欸哇')
d=json.load(open(sys.argv[1]));tok=d['text'].split();ts=d['ts']
for i,t in enumerate(tok):
    if t in F:
        print(f"{ts[i][0]/1000:.3f}\t{ts[i][1]/1000:.3f}\t{t}\t{''.join(tok[max(0,i-6):i])}【{t}】{''.join(tok[i+1:i+6])}")
