// TradingView 官方嵌入圖表（日線 K 線、深色）截圖 -> ../hf_final/assets/charts/<name>.png
// usage: PUPPETEER_PATH=... node chart_shot.mjs NVDA:NASDAQ:NVDA AMD:NASDAQ:AMD ...
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const puppeteer = require(process.env.PUPPETEER_PATH);
const out = path.resolve('../hf_final/assets/charts');
const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new',
  args: ['--lang=en-US', '--no-first-run'],
});
for (const arg of process.argv.slice(2)) {
  const [name, ex, sym] = arg.split(':');
  const q = new URLSearchParams({ symbol: `${ex}:${sym}`, interval: 'D', style: '1', theme: 'dark', locale: 'en',
    hidesidetoolbar: '1', hidetoptoolbar: '0', withdateranges: '0', saveimage: '0', toolbarbg: '131722', timezone: 'America/New_York'});
  const url = 'https://s.tradingview.com/widgetembed/?' + q.toString();
  const page = await browser.newPage();
  await page.setViewport({ width: +(process.env.VW||1100), height: +(process.env.VH||470), deviceScaleFactor: 3 });
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 90000 }).catch(e => console.log('warn', e.message));
  await new Promise(r => setTimeout(r, 6000));
  await page.screenshot({ path: path.join(out, name + '.png') });
  console.log('saved', name, url);
  await page.close();
}
await browser.close();
