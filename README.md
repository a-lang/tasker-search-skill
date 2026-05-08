# Tasker 案件搜尋 Skill

符合 [Agent Skills](https://agentskills.io/) 規範的 Tasker 案件搜尋工具，讓 AI Agent 能夠搜尋 tasker.com.tw 上的「我要接案」案件。

## 快速開始

### 安裝依賴

建議使用虛擬環境：

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
scrapling install
```

### 配置

```bash
cp .env.example .env
```

編輯 `.env`，填入登入資訊：

```
TASKER_ID=你的手機號碼或身分證字號
TASKER_PASSWORD=你的登入密碼
```

### 使用

```bash
# 搜尋特定關鍵字
python scripts/search.py --keywords "Linux,Asterisk" --top 5

# 獲取最新案件（不篩選關鍵字）
python scripts/search.py --top 10
```

**CLI 參數：**

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--keywords` | 搜尋關鍵字，多個用逗號分隔 | 空字串（不篩選） |
| `--top` | 返回案件數量 | 5（範圍 1-100） |

## 專案架構

```
tasker-search-skill/
├── scripts/search.py   # CLI 入口
├── scraper.py          # TaskerScraper 核心爬蟲
├── config.py           # Config 配置類
├── SKILL.md            # Agent Skills 規範定義
├── references/         # CSS 選擇器與技術參考
├── .env.example        # 環境變數範本
└── requirements.txt    # Python 依賴
```

輸出至 **stdout**（Markdown 格式），不寫檔案，方便 Agent 管道使用。

## 注意事項

- **登入欄位**：網站使用 `input[name="mobile"]`，不是 username
- **記住我**：預設啟用，Cookies 持久化到 `/tmp/tasker_user_data_[帳號]`；清除用 `rm -rf /tmp/tasker_user_data_*`
- **Lightbox 彈窗**：網站會自動彈出 `.box-lightbox` 遮擋頁面，程式會自動關閉
- **CSS 選擇器脆弱**：網站 HTML 結構可能變化，若提取失敗請檢查 `references/REFERENCE.md`

## 測試

需真實帳號與網路連線：

```bash
python test_login.py                                    # 測試登入
python test_remember_me.py                             # 測試持久化 Cookies
python test_search_accuracy.py                          # 搜尋結果正確性
python test_search_accuracy.py --keywords "Linux"       # 帶關鍵字搜尋
python test_search_accuracy.py --json                   # JSON 格式輸出
```

## 相關文件

- [SKILL.md](SKILL.md) — Skill 定義與使用說明
- [references/REFERENCE.md](references/REFERENCE.md) — CSS 選擇器參考
- [references/TECHNICAL.md](references/TECHNICAL.md) — 設計決策