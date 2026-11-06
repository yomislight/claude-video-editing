// Screen-record short clips of YouTube reports (muted) for B-roll.
// usage: PUPPETEER_PATH=/path/to/puppeteer-core OUT_DIR=../hf_final/assets/yt node yt_rec.mjs jobs.json
//   jobs: [{name, id, at:[sec,...], dur}]  → OUT_DIR/{name}_{at}.webm（之後用 yt_transcode.sh 轉 mp4）
// Only the player is visible; a clip is kept only if the video really advanced and no ad showed.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const puppeteer = require(process.env.PUPPETEER_PATH);
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = path.resolve(process.env.OUT_DIR || '../hf_final/assets/yt'); fs.mkdirSync(out, { recursive: true });
const browser = await puppeteer.launch({
  executablePath: process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: 'new', userDataDir: path.resolve('chrome-yt-profile'),
  args: ['--autoplay-policy=no-user-gesture-required', '--lang=en-US', '--window-size=1920,1080'],
});
const sleep = ms => new Promise(r => setTimeout(r, ms));
const adGone = async (page, secs = 120) => {
  for (let k = 0; k < secs; k++) {
    const ad = await page.evaluate(() => {
      const s = document.querySelector('.ytp-skip-ad-button, .ytp-ad-skip-button, .ytp-ad-skip-button-modern'); if (s) s.click();
      return !!document.querySelector('#movie_player.ad-showing');
    }).catch(() => false);
    if (!ad) return true; await sleep(1000);
  }
  return false;
};
const CSS = `html,body{overflow:hidden!important;background:#000!important}
  #masthead-container,#secondary,#below,#related,#comments,ytd-popup-container,tp-yt-iron-overlay-backdrop,ytd-mealbar-promo-renderer,#chat{display:none!important;visibility:hidden!important}
  #movie_player{position:fixed!important;left:0!important;top:0!important;width:1920px!important;height:1080px!important;z-index:2147483647!important;background:#000!important}
  #movie_player .html5-video-container,#movie_player video{position:absolute!important;left:0!important;top:0!important;width:1920px!important;height:1080px!important;object-fit:contain!important}
  .ytp-chrome-bottom,.ytp-chrome-top,.ytp-gradient-bottom,.ytp-gradient-top,.ytp-ce-element,.ytp-pause-overlay,.iv-branding,.ytp-paid-content-overlay,.ytp-spinner,.ytp-cards-teaser,.ytp-show-cards-title,.ytp-caption-window-container,.ytp-autonav-endscreen-countdown-overlay{display:none!important}`;
// every clip gets a fresh, normally-played page; on a player error we stop that clip rather than retry hard
for (const j of jobs) for (const at of j.at) {
  const file = path.join(out, `${j.name}_${at}.webm`);
  if (fs.existsSync(file) && fs.statSync(file).size > 0) { console.log(j.name, at, 'exists'); continue; }
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  try {
    await page.goto(`https://www.youtube.com/watch?v=${j.id}&t=${at}s`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await sleep(5000);
    if (!await adGone(page)) { console.log(j.name, at, 'FAIL ad'); continue; }
    await page.addStyleTag({ content: CSS });
    await page.evaluate(() => { const p = document.querySelector('#movie_player'), v = document.querySelector('video'); v.muted = true; try { p.mute(); p.setPlaybackQualityRange('hd1080', 'hd1080'); } catch (e) {} v.play().catch(() => {}); window.dispatchEvent(new Event('resize')); });
    let ok = false, err = false;
    for (let k = 0; k < 30 && !ok && !err; k++) {
      const a = await page.evaluate(() => document.querySelector('video').currentTime);
      await sleep(800);
      const b = await page.evaluate(() => ({ t: document.querySelector('video').currentTime, ad: !!document.querySelector('#movie_player.ad-showing'), e: !!document.querySelector('.ytp-error') }));
      err = b.e; if (b.ad) { await adGone(page); continue; }
      ok = b.t > a && b.t >= at - 1;
    }
    if (!ok) { console.log(j.name, at, err ? 'FAIL player-error' : 'FAIL not playing'); if (err) await sleep(30000); continue; }
    const t0 = await page.evaluate(() => document.querySelector('video').currentTime);
    const rec = await page.screencast({ path: file });
    await sleep(j.dur * 1000);
    await rec.stop();
    const q = await page.evaluate(() => { const v = document.querySelector('video'); return { w: v.videoWidth, h: v.videoHeight, t: v.currentTime, ad: !!document.querySelector('#movie_player.ad-showing') }; });
    const good = q.t - t0 > j.dur * .7 && !q.ad;
    if (!good) fs.rmSync(file, { force: true });
    console.log(j.name, at, good ? 'ok' : 'DROP', `${q.w}x${q.h} ${t0.toFixed(1)}->${q.t.toFixed(1)}`);
  } catch (e) { console.log(j.name, at, 'FAIL', e.message); }
  finally { await page.close(); await sleep(6000); }
}
await browser.close();
