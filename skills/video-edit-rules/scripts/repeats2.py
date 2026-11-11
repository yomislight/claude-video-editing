"""Wider repeat scan: (A) same 2+ token run again within 10 tokens, (B) doubled single token (stutter)."""
import json,sys
d=json.load(open(sys.argv[1]));tok=d['text'].split();ts=d['ts']
def mm(ms): s=ms/1000;return f"{int(s//60):02d}:{s%60:05.2f}"
OK2={'等等','看看','常常','谢谢','慢慢','刚刚','试试','想想','一一','个个','偏偏','往往','渐渐'}
seen=set()
for i in range(len(tok)-1):
    # A: bigram reappears soon
    bg=tok[i:i+2]
    for j in range(i+2,min(i+12,len(tok)-1)):
        if tok[j:j+2]==bg and (i,j) not in seen:
            seen.add((i,j))
            print(f"A {mm(ts[i][0])}\t{''.join(tok[max(0,i-5):i])}【{''.join(tok[i:j+2])}】{''.join(tok[j+2:j+7])}")
            break
    # B: doubled token
    if tok[i]==tok[i+1] and tok[i]+tok[i+1] not in OK2:
        print(f"B {mm(ts[i][0])}\t{''.join(tok[max(0,i-5):i])}【{tok[i]}{tok[i+1]}】{''.join(tok[i+2:i+7])}")
