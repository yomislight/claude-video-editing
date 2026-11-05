"""check/final.srt -> caps.json: script-corrected Simplified text (the display font draws Traditional shapes from it)."""
import re,json
FIX=[('Cloud Code','Claude Code'),('Cloud','Claude'),('cloud','Claude'),('幽冥老师','yomi老师'),('这条系统','这套系统'),('整只影片','整支影片'),('桌面板','桌面版'),('Paracade','Parakeet'),('剪印规范','剪辑规范'),('剪印','剪映'),('HeyGene','HeyGen'),('捡到哪里','剪到哪里'),('资料源','资料员'),('FM Page','FFmpeg'),('OpenScreen','Openscreen'),('不强我们','不抢我们'),('没剪一支','每剪一支'),('一直长达','一支长达'),('我看完他给的几条意见','我看完给它几条意见'),('录屏我和','录屏幕和'),('把画剪顺','把话剪顺'),('Premium','Premiere'),('Hyperframes','HyperFrames'),('压的','压得'),('讲的最','讲得最'),('做的完美','做得完美'),('Skills','Skills'),('skills','Skills'),('skill','Skill'),('他','它'),('幕的颜色','幕的颜色'),('Crypto','crypto'),('这只影片','这支影片'),('这一只影片','这一支影片')]
ACC=['Claude Code','Claude','Whisper','HyperFrames','FFmpeg','Openscreen','Parakeet','Epidemic Sound','GitHub','Skills','Skill','Pro','369刀','43分钟','16分钟','22美元','200美元','听写员','动画师','资料员','质检员','音效师','剪辑师','时间码','时间线','七个角色','剪辑规范','真实的截图','免费','零','速度','最后一条','0.2秒','成本']
b=open('check/final.srt',encoding='utf8').read().strip().split('\n\n')
def t(x):
    h,m,s=x.split(':');return int(h)*3600+int(m)*60+float(s.replace(',','.'))
out=[]
for x in b:
    l=x.split('\n');a,e=l[1].split(' --> ');s=''.join(l[2:]).strip()
    for p,q in FIX:s=s.replace(p,q)
    out.append({'s':t(a),'e':t(e),'t':s})
for i in range(len(out)-1): out[i]['e']=min(out[i]['e'],out[i+1]['s'])
out[-1]['e']=421.6
json.dump({'caps':out,'acc':ACC},open('caps.json','w'),ensure_ascii=False,indent=0)
print(len(out));print('\n'.join(f"{c['s']:.1f} {c['t']}" for c in out if len(c['t'])>18))
print(sorted(set(''.join(c['t'] for c in out))&set('后干松准只台面里范系制发复板云谷斗冲钟须历划丑几')))
