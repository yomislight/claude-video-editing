import sys,glob
from funasr import AutoModel
m=AutoModel(model="paraformer-zh",vad_model="fsmn-vad",disable_update=True,disable_pbar=True)
for f in sorted(glob.glob(sys.argv[1])):
    print(f.split('/')[-1], m.generate(input=f)[0]['text'].replace(' ',''))
