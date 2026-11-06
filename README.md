# Claude 影片剪輯系統

用 Claude Code 剪輯口播長影片的完整工作流程與規範。除了 Claude 會員，其餘工具全部免費。

![Claude Code](https://img.shields.io/badge/Claude_Code-workflow-5EEAD4) ![HyperFrames](https://img.shields.io/badge/HyperFrames-composition-6366F1) ![FFmpeg](https://img.shields.io/badge/FFmpeg-render-007808) ![License: MIT](https://img.shields.io/badge/License-MIT-blue)

這個倉庫整理了兩支影片的真實製作過程：

- **Claude 剪輯教程**：7 分鐘的教學影片。12:53 的原始口播粗剪成 7:02，共 182 刀，再加上字幕、動畫、截圖、配樂與音效。
- **幣安 63 億被盜拆解**：16:40 的新聞事件長片，有精彩預告、片頭、新聞錄屏、X 推文證據和攻擊鏈圖，並寫好詳情頁、章節和封面。

## 內容

```text
.
├── skills/video-edit-rules/   可直接交給 Claude 的剪輯規範（Skill）
│   ├── SKILL.md               規範與完整流程
│   ├── assets/style.css       視覺樣式
│   └── scripts/               粗剪、匯出、人臉定位、網頁截圖腳本
├── skills/news-event-longform/  新聞事件長片流程（Skill）
│   ├── SKILL.md               預告結構、真實素材、渲染、詳情頁、章節、封面
│   ├── scripts/               新聞錄屏、推文截圖、串流渲染、章節檢查、封面抽圖
│   └── templates/             詳情頁模板、封面提示詞模板（中文）
├── episodes/binance-hack/     幣安被盜那一集：B-roll 與成片建置腳本、腳本、剪輯單、詳情頁
├── episode/                   Claude 剪輯教程那一集的成片工程來源
│   ├── build_full.py          產生 HyperFrames 時間線
│   ├── final.css              成片樣式
│   ├── caps.json              校正後的字幕
│   ├── edl.txt                粗剪剪輯單
│   └── targets.json           截圖網址清單
└── docs/                      腳本、拍攝清單、B-roll 清單、剪輯單
```

## 快速開始

1. 安裝 [Claude Code](https://claude.com/product/claude-code)、[FFmpeg](https://ffmpeg.org/)、[whisper.cpp](https://github.com/ggml-org/whisper.cpp) 與 [HyperFrames](https://github.com/heygen-com/hyperframes)。
2. 把 `skills/video-edit-rules`（和要做新聞事件長片時的 `skills/news-event-longform`）複製到 `~/.claude/skills/`。
3. 把素材和腳本放進同一個資料夾，對 Claude 說：

   ```text
   照著剪輯規範，幫我把這條素材粗剪出來。
   ```

4. 帶著時間碼給意見，最後說「把你剛剛學到的記進剪輯規範」。

## 工作流程

```mermaid
flowchart LR
  A[腳本] --> B[拍攝]
  B --> C[轉寫]
  C --> D[粗剪]
  D --> E[B-roll 清單]
  E --> F[風格樣片]
  F --> G[全片動畫]
  G --> H[渲染與質檢]
  H --> I[不公開上傳]
```

每一步都由人確認後才往下走。詳細規則見 [SKILL.md](skills/video-edit-rules/SKILL.md)。

## 七個角色

| 角色 | 工具 | 費用 |
|---|---|---|
| 剪輯師 | [Claude Code](https://claude.com/product/claude-code) | Claude Pro（月付 $22，日本區含稅，2026-11-05） |
| 聽寫員 | [Whisper](https://github.com/openai/whisper) | 免費 |
| 動畫師 | [HyperFrames](https://github.com/heygen-com/hyperframes) | 免費 |
| 資料員 | 瀏覽器（真實網頁截圖） | 免費 |
| 錄屏 | [Openscreen](https://github.com/siddharthvaddem/openscreen)（倉庫已於 2026-10-17 封存，不再更新） | 免費 |
| 音效師 | YouTube 音樂庫、[Mixkit](https://mixkit.co/free-sound-effects/) | 免費 |
| 質檢員 | [FFmpeg](https://ffmpeg.org/) | 免費 |

## 重建這一集

`episode/build_full.py` 需要原始素材才能執行。素材不在此倉庫，請換成你自己的影片、字幕、Logo 與字型。它是可參考的範例，不是開箱即用的工具。

`skills/video-edit-rules/scripts/` 依賴本機環境，部分腳本的參數尚未在其他專案上實測，首次使用可能需要小幅調整。

## 新聞事件長片

```mermaid
flowchart LR
  A[定剪] --> B[B-roll 提示表]
  B --> C[新聞錄屏與推文證據]
  C --> D[預告＋片頭＋正文]
  D --> E[串流渲染]
  E --> F[詳情頁與章節]
  F --> G[封面]
```

詳見 [news-event-longform/SKILL.md](skills/news-event-longform/SKILL.md)。新聞片段僅作評論引用，上傳時可能觸發 Content ID。

## 未收錄的內容

下列內容因版權或檔案大小未放入此倉庫：

- 原始影片、錄屏、新聞片段與成片
- 字型（汉仪节奏黑等商業字型請自行取得授權）
- 音樂、音效、Logo 與網頁截圖

## 致謝

流程架構受 Christian Peverelli 的影片 [I Fully Automated My Video Editing Using Claude Code](https://youtu.be/HzXD4GVqXwM) 啟發。

## 授權

本倉庫的程式碼與文件採用 [MIT License](LICENSE)。第三方工具與品牌名稱歸各自所有者。
