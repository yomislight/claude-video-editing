// 截取推文的官方嵌入卡（深色），當作「真實證據」素材。不需要登入 X。
// usage: PUPPETEER_PATH=/path/to/puppeteer-core node x_shot.mjs out_dir name:tweetId [name:tweetId ...]
// 例：node x_shot.mjs ../hf_final/assets/shots x_suspend:2115981055043981791
// 推文 ID 先在 X 上用 `from:帳號 -filter:replies since:YYYY-MM-DD until:YYYY-MM-DD` 搜到（搜尋要登入）。
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const puppeteer = require(process.env.PUPPETEER_PATH);
const [out, ...pairs] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const b = await puppeteer.launch({ executablePath: process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--lang=en-US'] });
const sleep = ms => new Promise(r => setTimeout(r, ms));
for (const pair of pairs) {
  const [name, id] = pair.split(':');
  const p = await b.newPage(); await p.setViewport({ width: 620, height: 900, deviceScaleFactor: 2.5 });
  await p.goto(`https://platform.twitter.com/embed/Tweet.html?id=${id}&theme=dark&lang=en&dnt=true`, { waitUntil: 'networkidle2', timeout: 60000 }).catch(() => {});
  await sleep(3000);
  console.log(name, JSON.stringify(await p.evaluate(() => document.body.innerText.slice(0, 400))));
  const el = await p.$('article') || await p.$('#app');
  await el.screenshot({ path: path.join(out, `${name}.png`) });
  await p.close();
}
await b.close();
