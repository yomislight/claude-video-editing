"""Verbatim Chinese ASR (FunASR Paraformer) with per-char timestamps -> JSON. usage: fasr.py in.wav out.json"""
import sys,json
from funasr import AutoModel
m=AutoModel(model="paraformer-zh",vad_model="fsmn-vad",disable_update=True,disable_pbar=True)
r=m.generate(input=sys.argv[1],batch_size_s=300)[0]
toks=r['text'].split(' ') if ' ' in r['text'] else list(r['text'].replace(' ',''))
json.dump({'text':r['text'],'ts':r['timestamp']},open(sys.argv[2],'w'),ensure_ascii=False)
print(r['text'][:400])
