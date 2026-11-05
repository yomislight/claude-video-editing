// Screenshot official pages for B-roll; record where the key sentence sits so the video can highlight it.
// usage: node capture.mjs targets.json  -> ../hf_final/assets/shots/<name>.png + shots.json
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const puppeteer = require(process.env.PUPPETEER_PATH);

const targets = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = path.resolve('../hf_final/assets/shots');
const metaPath = path.join(outDir, 'shots.json');
const meta = fs.existsSync(metaPath) ? JSON.parse(fs.readFileSync(metaPath, 'utf8')) : {};

const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: 'new',
  args: ['--lang=en-US', '--disable-blink-features=AutomationControlled', '--no-first-run'],
  userDataDir: path.resolve('chrome-shot-profile'),
});

for (const t of targets) {
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36');
  try {
    await page.goto(t.url, { waitUntil: 'networkidle2', timeout: 60000 });
  } catch (e) { console.log('load warn', t.name, e.message); }
  await new Promise(r => setTimeout(r, t.wait || 2500));
  // reject optional cookies where offered (privacy-preserving), else close the banner
  await page.evaluate(() => {
    const btns = [...document.querySelectorAll('button, a[role=button]')];
    const pick = btns.find(b => /reject (all|additional)|decline|only necessary|necessary only|拒绝/i.test(b.innerText));
    if (pick) pick.click();
  }).catch(() => {});
  await new Promise(r => setTimeout(r, 800));
  // hide floating dialogs / banners / paywalls without accepting anything
  await page.evaluate(() => {
    const vw = innerWidth, vh = innerHeight;
    for (const el of document.querySelectorAll('body *')) {
      const cs = getComputedStyle(el);
      if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
      const r = el.getBoundingClientRect();
      const big = r.width * r.height > vw * vh * 0.15;
      const bottomBar = r.top > vh * 0.6 && r.width > vw * 0.5;
      const isHeader = r.top <= 1 && r.height < 120;
      if ((big || bottomBar) && !isHeader) el.style.setProperty('display', 'none', 'important');
    }
    document.documentElement.style.overflow = 'auto'; document.body.style.overflow = 'auto';
  }).catch(() => {});
  if (t.hide) await page.addStyleTag({ content: `${t.hide} { display: none !important; }` }).catch(() => {});
  // locate the key sentence
  let rect = null;
  if (t.find) {
    rect = await page.evaluate((needle) => {
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        const i = node.textContent.indexOf(needle);
        if (i >= 0 && node.parentElement && node.parentElement.offsetParent !== null) {
          node.parentElement.scrollIntoView({ block: 'center' });
          const range = document.createRange();
          range.setStart(node, i); range.setEnd(node, i + needle.length);
          const rs = [...range.getClientRects()].map(r => ({ x: r.x, y: r.y, w: r.width, h: r.height }));
          return rs;
        }
      }
      return null;
    }, t.find);
    await new Promise(r => setTimeout(r, 600));
    if (rect) {  // re-measure after scroll settles
      rect = await page.evaluate((needle) => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let node;
        while ((node = walker.nextNode())) {
          const i = node.textContent.indexOf(needle);
          if (i >= 0 && node.parentElement && node.parentElement.offsetParent !== null) {
            const range = document.createRange();
            range.setStart(node, i); range.setEnd(node, i + needle.length);
            return [...range.getClientRects()].map(r => ({ x: r.x, y: r.y, w: r.width, h: r.height }));
          }
        }
        return null;
      }, t.find);
    }
  } else if (t.scrollY) {
    await page.evaluate(y => window.scrollTo(0, y), t.scrollY);
    await new Promise(r => setTimeout(r, 600));
  }
  const file = path.join(outDir, `${t.name}.png`);
  await page.screenshot({ path: file });
  const title = await page.title();
  meta[t.name] = { url: t.url, title, find: t.find || null, rects: rect, vw: 1440, vh: 900, captured: new Date().toISOString() };
  console.log(t.name, '|', title.slice(0, 70), '|', t.find ? (rect ? `found ${rect.length} rect(s)` : 'NOT FOUND') : 'top');
  await page.close();
}
await browser.close();
fs.writeFileSync(metaPath, JSON.stringify(meta, null, 1));
