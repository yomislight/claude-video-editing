"""Print FunASR chars with absolute source times for source windows given as start-end args."""
import sys,subprocess,json
from funasr import AutoModel
m=AutoModel(model="paraformer-zh",vad_model="fsmn-vad",disable_update=True,disable_pbar=True)
for w in sys.argv[2:]:
    a,b=map(float,w.split('-'))
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(a),'-to',str(b),'-i',sys.argv[1],'probe/sc.wav'],check=True)
    r=m.generate(input='probe/sc.wav')[0]
    print(w,' '.join(f"{t}@{a+s/1000:.2f}-{a+e/1000:.2f}" for t,(s,e) in zip(r['text'].split(),r['timestamp'])))
