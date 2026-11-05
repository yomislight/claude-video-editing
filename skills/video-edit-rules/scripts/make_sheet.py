"""Write ../剪辑单.md from segments.json, report.json and edl.txt."""
import json,re
d=json.load(open('segments.json'));fps=d['fps'];segs=d['segments'];rep=json.load(open('report.json',encoding='utf8'))
F=eval(re.search(r"FIX=(\[.*?\])\n",open('make_hf.py',encoding='utf8').read()).group(1))
def fx(t):
    for a,b in F: t=t.replace(a,b)
    return t
off=0;MAP=[]
for a,b,l in segs:
    MAP.append((a,b,off));off+=b-a
def cut(fr):
    for a,b,o in MAP:
        if a-3<=fr<=b: return o+max(fr-a,0)
    return None
SP={}
for r in rep:
    fi,fo=round(r['in']*fps),round(r['out']*fps)
    if r['line'] not in SP: SP[r['line']]=[cut(fi),fi,fo]
    else: SP[r['line']][2]=fo
def tc(f):
    s=f/fps;return f"{int(s//60):02d}:{s%60:05.2f}"
tx={}
for r in rep: tx[r['line']]=tx.get(r['line'],'')+('｜' if r['line'] in tx else '')+fx(r['text'])
heads={};cnt=-1
for raw in open('edl.txt',encoding='utf8'):
    x=raw.strip()
    if x.startswith('# ---'): heads[cnt+1]=x.strip('# -')
    elif x and not x.startswith('#'): cnt+=1
o=[f"# 剪辑单\n\n成片长度 **{tc(off)}**，共 {len(segs)} 个片段（原素材 12:53）。\n\n每行一句：成片时间 ← 原素材时间 ｜ 实际保留的话（错别字已按脚本校正，声音不变）。\n"]
for l in sorted(SP):
    if l in heads:o.append(f"\n## {heads[l]}\n\n| 成片 | 原素材 | 内容 |\n|---|---|---|")
    st,a,b=SP[l];o.append(f"| {tc(st)} | {tc(a)}–{tc(b)} | {tx[l]} |")
open('../剪辑单.md','w',encoding='utf8').write('\n'.join(o)+'\n');print(tc(off),len(segs))
