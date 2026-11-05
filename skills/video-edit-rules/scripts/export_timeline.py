"""Export segments.json as FCPXML (Final Cut Pro / DaVinci Resolve) and
FCP7 XML (Premiere Pro / DaVinci Resolve), both pointing at the original MOV."""
import json, os, urllib.parse
from xml.sax.saxutils import escape

d = json.load(open('segments.json'))
fps, segs = d['fps'], d['segments']
SRC = os.path.abspath(os.environ.get('SRC', '../source.mp4'))
BASE = os.path.basename(SRC).rsplit('.', 1)[0]
URL = 'file://' + urllib.parse.quote(SRC)
SRC_FRAMES = int(os.environ['SRC_FRAMES'])  # ffprobe -count_packets 得到原片总帧数
NAME = os.environ.get('NAME', 'rough_cut')
total = sum(b - a for a, b, _ in segs)

# ---------- FCPXML 1.10 ----------
clips, off = [], 0
for k, (a, b, line) in enumerate(segs):
    clips.append(f'        <asset-clip ref="r2" name="{BASE} #{k+1}" offset="{off}/{fps}s" '
                 f'start="{a}/{fps}s" duration="{b-a}/{fps}s" format="r1" tcFormat="NDF" audioRole="dialogue"/>')
    off += b - a
fcpxml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.10">
  <resources>
    <format id="r1" name="FFVideoFormat1080p30" frameDuration="1/{fps}s" width="1920" height="1080" colorSpace="1-1-1 (Rec. 709)"/>
    <asset id="r2" name="{BASE}" start="0s" duration="{SRC_FRAMES}/{fps}s" hasVideo="1" format="r1" hasAudio="1" audioSources="1" audioChannels="2" audioRate="48000">
      <media-rep kind="original-media" src="{URL}"/>
    </asset>
  </resources>
  <library>
    <event name="{NAME}">
      <project name="{NAME}">
        <sequence format="r1" duration="{total}/{fps}s" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
          <spine>
{chr(10).join(clips)}
          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
'''
open(f'../{NAME}.fcpxml', 'w', encoding='utf-8').write(fcpxml)

# ---------- FCP7 XML (xmeml v4) ----------
def rate():
    return f'<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>'

def file_el(first):
    if not first:
        return '<file id="file-1"/>'
    return f'''<file id="file-1"><name>{os.path.basename(SRC)}</name><pathurl>{escape(URL)}</pathurl>{rate()}<duration>{SRC_FRAMES}</duration>
<media><video><samplecharacteristics>{rate()}<width>1920</width><height>1080</height></samplecharacteristics></video>
<audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>2</channelcount></audio></media></file>'''

v_items, a1_items, a2_items, off = [], [], [], 0
for k, (a, b, line) in enumerate(segs):
    n = k + 1
    common = (f'<name>{BASE} #{n}</name><enabled>TRUE</enabled><duration>{SRC_FRAMES}</duration>{rate()}'
              f'<start>{off}</start><end>{off + b - a}</end><in>{a}</in><out>{b}</out>')
    links = ''.join(f'<link><linkclipref>{t}-{n}</linkclipref><mediatype>{m}</mediatype><trackindex>{ti}</trackindex><clipindex>{n}</clipindex>{"" if m=="video" else f"<groupindex>1</groupindex>"}</link>'
                    for t, m, ti in (('v', 'video', 1), ('a1', 'audio', 1), ('a2', 'audio', 2)))
    v_items.append(f'<clipitem id="v-{n}">{common}{file_el(k == 0)}{links}</clipitem>')
    for lst, t, ch in ((a1_items, 'a1', 1), (a2_items, 'a2', 2)):
        lst.append(f'<clipitem id="{t}-{n}">{common}<file id="file-1"/>'
                   f'<sourcetrack><mediatype>audio</mediatype><trackindex>{ch}</trackindex></sourcetrack>{links}</clipitem>')
    off += b - a

xmeml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
<sequence id="seq-1"><name>{NAME}</name><duration>{total}</duration>{rate()}
<timecode>{rate()}<string>00:00:00:00</string><frame>0</frame><displayformat>NDF</displayformat></timecode>
<media>
<video><format><samplecharacteristics>{rate()}<width>1920</width><height>1080</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format>
<track>{''.join(v_items)}</track></video>
<audio><numOutputChannels>2</numOutputChannels>
<track>{''.join(a1_items)}<outputchannelindex>1</outputchannelindex></track>
<track>{''.join(a2_items)}<outputchannelindex>2</outputchannelindex></track></audio>
</media></sequence>
</xmeml>
'''
open(f'../{NAME}_Premiere.xml', 'w', encoding='utf-8').write(xmeml)
print(len(segs), 'clips', total / fps, 's')
