"""成片 HTML 繁体化。
汉仪节奏黑（Jiezou）要输入简体才显示繁体字形，所以源文字一律写简体；
这里给页面加一段脚本：渲染前按每段文字实际用的字体处理——
  - 不是 Jiezou 的（PuHui、截图标注、小字）：整段换成 opencc s2tw 的繁体；
  - 是 Jiezou 的：保留简体，只把一简多繁的字（后干松准线）换成 <u>繁体</u>（MiSans 补字）。
"""
import sys, re, json, html
from html.parser import HTMLParser
import opencc

CC = opencc.OpenCC('s2tw')
CJK = re.compile(r'[一-鿿]')
p = sys.argv[1]
src = open(p, encoding='utf-8').read()
src = re.sub(r'\n<script id="trad">.*?</script>\n', '\n', src, flags=re.S)
body = src[src.index('<div id="root"'):src.rindex('<script>')]

texts = set()
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.skip = 0
    def handle_starttag(s, t, a):
        if t in ('script', 'style'): s.skip += 1
    def handle_endtag(s, t):
        if t in ('script', 'style'): s.skip -= 1
    def handle_data(s, d):
        if not s.skip and CJK.search(d): texts.add(d)
P().feed(body)
M = {t: CC.convert(t) for t in texts}
M = {k: v for k, v in M.items() if k != v}
js = '''
<script id="trad">
(function(){const M=%s;const ONE="后干松准线么里";
const w=document.createTreeWalker(document.getElementById("root"),NodeFilter.SHOW_TEXT);const ns=[];while(w.nextNode())ns.push(w.currentNode);
for(const n of ns){const s=n.nodeValue,t=M[s];if(!t)continue;const el=n.parentElement;
if(getComputedStyle(el).fontFamily.indexOf("Jiezou")<0){n.nodeValue=t;continue;}
if(t.length!==s.length)continue;let hit=false;for(const c of ONE)if(s.includes(c))hit=true;if(!hit)continue;
const f=document.createDocumentFragment();let buf="";
for(let i=0;i<s.length;i++){const c=s[i];if(ONE.includes(c)&&t[i]!==c){if(buf){f.append(buf);buf="";}const u=document.createElement("u");u.textContent=t[i];f.append(u);}else buf+=c;}
if(buf)f.append(buf);n.replaceWith(f);}})();
</script>
''' % json.dumps(M, ensure_ascii=False)
i = src.rindex('<script>')
src = src[:i] + js.lstrip('\n') + src[i:]
open(p, 'w', encoding='utf-8').write(src)
print(f'trad: {len(M)} text nodes mapped')
