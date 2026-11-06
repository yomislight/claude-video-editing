---
name: news-event-longform
description: 加密未來頻道「新聞事件拆解」長片的全流程：口播粗剪定稿後，按腳本做 B-roll（真實新聞錄屏、X 推文證據、官方 logo、網頁截圖、攻擊鏈圖），組成預告＋片頭＋正文的 HyperFrames 成片，串流渲染、質檢，再寫標題、詳情頁、章節和封面提示詞。使用者要做幣安被盜這類事件長片、要錄新聞畫面、找推文證據、渲染長片、寫詳情頁或章節時，先讀這份檔案。剪輯基本規範見 video-edit-rules。
---

# 新聞事件長片（加密未來）

範例：`episodes/binance-hack/`（幣安 63 億被盜，16:40，2026-11）。
基本剪輯規範（粗剪、字幕、聲音、質檢）沿用 `skills/video-edit-rules/SKILL.md`，這裡只寫事件長片多出來的部分。

## 規範速查

- 每一步使用者確認後才往下：腳本 → 粗剪 → B-roll 提示表 → 全片 → 渲染 → 標題詳情頁 → 封面
- 說到什麼就出什麼；只用真實素材：官方公告、官方推文、新聞錄屏、鏈上數據。絕不編造推文或新聞卡
- 投資題材只分析事件，不給觀點
- Logo、人像位置在 Studio 裡調好後，**寫回建置腳本**，否則下次重建會被蓋掉
- 長片渲染一律 `--workers 1`
- 詳情頁一律另存成純文字 `.txt`，章節才不會丟換行
- 生圖提示詞一律中文
- 回覆使用者用中文

## 一、工作順序

| 步驟 | 做什麼 | 產出 |
|---|---|---|
| 1 | 用使用者的 SRT 和腳本粗剪（不重新轉寫），選最後一條講完整的 | `粗剪_*.mp4`、FCPXML、Premiere XML |
| 2 | 使用者給時間碼意見，改到定剪 | `定剪_*.mp4`、`剪輯單.md` |
| 3 | 按句列 B-roll：時間碼、口播、素材類型、來源 | `B-roll提示表.md` |
| 4 | 收集真實素材：新聞錄屏、推文、官方網頁、logo | `hf_final/assets/` |
| 5 | 組全片，Studio 開著讓使用者邊看邊改 | `hf_final/index.html` |
| 6 | 使用者說可以了才渲染 | `成片_*.mp4` |
| 7 | 標題、詳情頁、章節 | `標題與簡介.md`、`詳情頁.txt` |
| 8 | 封面：抽人物圖 + 中文提示詞 | `封面素材/` |

## 二、成片結構

```text
預告1 | 預告2 | 開場 hook（到「一起看下去吧」）| Crypto Future 片頭 4s | 正文 | 感謝觀看卡
```

- 時間換算：`T(t) = TEASE + t + (STING if t >= SPLIT)`，`TEASE` 是兩段預告總長，`SPLIT` 是片頭插入點。所有 B-roll 都用定剪時間寫，再用 `T()` 換到成片時間。
- A-roll 畫面用**美顏版**，聲音用定剪原聲；兩者幀數必須一致。
- 預告的人像要夠大、比例正確；中間不能只閃一幀人物，要嘛整段放人，要嘛整段放素材。
- 頻道 logo 全片同一個位置（右上），座標只寫在 `build_final.py` 的 `.logo` 一處。
- 網頁視窗、圖卡不能壓到 logo 和字幕；圖塊文字設 `white-space:nowrap`，不准折行。
- 場景加 `outline:8px solid <底色>`，避免 Studio 預覽邊緣露白。

## 三、真實素材

### 新聞錄屏（YouTube）
1. 找 CNN、DW、FRANCE 24、Bloomberg 這類電視台的公開報導，記下影片 ID 和要用的秒數。
2. 寫 `ytjobs.json`：`[{"name":"cnn","id":"<影片ID>","at":[10,30],"dur":8}]`
3. 錄：`PUPPETEER_PATH=… OUT_DIR=../hf_final/assets/yt node scripts/yt_rec.mjs ytjobs.json`
   - 每個片段開一個新分頁，從 `&t=` 正常播放。不要在同一頁快速跳轉，會拿到舊畫面，還會觸發 YouTube「出了點問題」。
   - 片段之間停 6 秒；遇到廣告就等它結束；確認播放時間真的有前進才算數。
   - 只留播放器畫面，隱藏側欄、控制列、字幕。
4. 轉檔：`scripts/yt_transcode.sh ../hf_final/assets/yt yt_raw`（`-g 15` 讓 seek 準）。
5. 每段都要抽幀確認內容和口播對得上。例：口播講「另一種方式」，卻配到手機特寫，就換成專家訪談。
6. 畫面放在「監看器」框裡，上方寫「畫面來源：電視台」。詳情頁另列新聞畫面來源。
7. 提醒使用者：新聞片段可能觸發 Content ID。

### X 推文證據
1. 在瀏覽器登入 X（請使用者自己登入），搜尋：`from:binance -filter:replies since:2026-10-29 until:2026-10-31`。
2. 截官方嵌入卡（不需登入）：`node scripts/x_shot.mjs ../hf_final/assets/shots x_suspend:<推文ID>`。
3. 高亮框按縮放比例換算，寬度不能蓋到下一個字。
4. 口播和推文說法不一致時要告訴使用者。例：口播說「停止交易」，推文其實是「暫停充值、提現」。

### Logo 與網頁
- 用官方 logo（Wikimedia 或官網），PNG 透明底，至少 480px。
- 網頁截圖照 `video-edit-rules` 的做法，拒絕非必要 Cookie。裁切不能把英文單字切一半。

## 四、Studio 與重建

- 預覽：`hyperframes preview hf_final --port 3003 --foreground --no-open`，打不開就重啟這個 server。
- 使用者在 Studio 拖過的位置（`translate`、寬高、`data-hf-studio-*`），先讀出數值，寫進 `build_final.py` 或 `broll2.py`，再重建。
- 改之前先備份：`broll2_vN.py`、`build_final_vN.py`。
- `hyperframes check` 的 `text_occluded` 若全來自背景字元雨，可以忽略。彙報時要如實說有幾個、來自哪裡，不能說 0 錯誤。

## 五、渲染

```bash
scripts/render_stream.sh hf_final /path/成片_xxx.mp4
```

- **必須 `--workers 1`。** 多 worker 會先把所有幀寫進硬碟，16 分鐘需要約 28GB。`--start/--end` 分段會撞 2GB 的 PLAN_TOO_LARGE。
- 渲染前清 extract cache：`$(getconf DARWIN_USER_TEMP_DIR)hyperframes-extract-cache-501`，它可能堆到 9–18GB。
- 16 分鐘大約要跑 1–2 小時，要在背景跑。
- 渲染完檢查這幾項：
  - 1920×1080 30fps
  - 時長與預期一致
  - 平均音量約 -18dB，峰值低於 -1.5dB
  - 沒有 3 秒以上的靜音
  - 抽幀看 logo、字幕、人臉

## 六、標題、詳情頁、章節

- **標題：** 寫反轉和數字，例如「私鑰沒丟，錢卻被轉走？幣安 63 億被盜全流程拆解」。再給 3 個備選。
- **詳情頁：** 照 `templates/詳情頁模板.txt`，裡面有推廣連結、TG、正文、章節、資料來源、新聞畫面來源、往期、免責、hashtag。
- **章節規則：**
  - 每個時間點單獨一行，寫在行首
  - 第一個是 `0:00`
  - 至少 3 章，每章至少 10 秒
  - 章節名不以數字開頭
- 詳情頁存成 `詳情頁.txt`，請使用者從 txt 複製；從 Markdown 預覽複製會丟換行，YouTube 就認不出章節。
- 檢查：`python3 scripts/check_chapters.py 詳情頁.txt <片長秒數>`
- 章節時間要從成片時間算，也就是要加上預告和片頭。

## 七、封面

- 照 `templates/封面提示詞模板.md`：
  - 人物在右，左上放主角 logo，加箭頭
  - 下方兩行大字，第二行最大
- 人物圖：`scripts/stills.sh <美顏版.mp4> 封面素材 微笑 25 25.5 36 971.75`，抽 4 張給使用者挑。選半身、微笑有親和感、帶手勢的。
- 提示詞給兩版，**全部中文**：
  - A 版無字底圖（推薦），字之後再加
  - B 版帶字
- 涉及國家歸因的事件，用兜帽剪影，不放國旗、不放真人。

## 八、交付資料夾

```text
<專案>/
├── 成片_<主題>.mp4
├── 標題與簡介.md / 詳情頁.txt
├── 封面素材/封面人物.png
├── 腳本.txt / 剪輯單.md / B-roll提示表.md
├── 工程檔/（FCPXML、Premiere XML）
├── 過程檔/（粗剪、定剪 mp4）
├── hf_final/（HyperFrames 成片工程）
└── work/（建置腳本；舊版本放 work/_old）
```

## 九、腳本

| 檔案 | 作用 |
|---|---|
| `scripts/yt_rec.mjs` | YouTube 新聞錄屏：一段一頁，跳過廣告，驗證有播放 |
| `scripts/yt_transcode.sh` | webm 轉成好 seek 的 mp4 |
| `scripts/x_shot.mjs` | 推文官方嵌入卡截圖（深色） |
| `scripts/render_stream.sh` | 串流渲染 + 質檢 |
| `scripts/check_chapters.py` | 檢查 YouTube 章節格式 |
| `scripts/stills.sh` | 抽封面人物圖 + 預覽拼圖 |
| `episodes/binance-hack/broll2.py` | 本期所有 B-roll 元件與時間點（`kw`、`tiles`、`web`、`yt`、`graph`、`rows`） |
| `episodes/binance-hack/build_final.py` | 組成片：預告、片頭、正文、字幕、logo、音樂 |

依賴：
- FFmpeg
- HyperFrames CLI
- Node + puppeteer-core（設 `PUPPETEER_PATH`）
- Google Chrome
- Python 3
