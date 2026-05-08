# AGENTS.md

## 語言

始終使用繁體中文回覆。

## 專案概覽

Tasker 案件搜尋 Skill — 使用 Scrapling/Playwright 自動化爬取 tasker.com.tw 案件。符合 Agent Skills 規範（見 `SKILL.md`）。

## 環境設定

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
scrapling install               # 必須，安裝瀏覽器及其依賴
cp .env.example .env           # 填入 TASKER_ID 和 TASKER_PASSWORD
```

.env 必填：`TASKER_ID`、`TASKER_PASSWORD`。缺少會在 `Config.validate()` 拋錯。

## 執行

```bash
python scripts/search.py --keywords "Linux,Asterisk" --top 5
python scripts/search.py --top 10                 # 不篩選關鍵字
```

## 架構

- `scripts/search.py` — CLI 入口，`--keywords` 和 `--top` 參數
- `scraper.py` — `TaskerScraper` 類，核心爬蟲邏輯
- `config.py` — `Config` 類，從 `.env` 讀取設定
- `SKILL.md` — Agent Skills 規範定義
- `references/REFERENCE.md` — CSS 選擇器參考
- `references/TECHNICAL.md` — 設計決策

## 特殊注意事項

- **「記住我」功能**：預設啟用，Cookies 持久化到 `/tmp/tasker_user_data_[帳號]`。清除用 `rm -rf /tmp/tasker_user_data_*`
- **登入欄位**：網站用 `input[name="mobile"]`，不是 username
- **輸出**：結果輸出到 stdout，不寫檔案（這是有意設計，方便 Agent 管道使用）
- **CSS 選擇器脆弱**：tasker.com.tw 的 HTML 結構可能變化，選擇器在 `references/REFERENCE.md` 有清單。若提取失敗，先檢查選擇器是否仍有效
- **時間解析**：`_parse_time_for_sort` 支援完整日期(`YYYY/MM/DD`)、天數前(`N天前`)、小時前(`N小時前`)、分鐘前(`N分鐘前`)、今天(`今天 HH:MM`)、昨天(`昨天 HH:MM`)
- **Lightbox 彈窗**：網站會自動彈出 `.box-lightbox` 彈窗遮擋頁面，所有頁面互動（登入、搜尋、案件詳情）前都必須先關閉。`_dismiss_lightbox` 方法會嘗試點擊關閉按鈕或用 JS 隱藏
- **登入檢查**：`search_and_output` 會先檢查是否已登入（`_check_logged_in`），已登入則跳過登入流程
- **案件 ID 格式**：URL 過濾使用正則 `/cases/TK[A-Za-z0-9]+` 確保只匹配真實案件
- **資料來源標記**：`budget` 和 `location` 欄位有對應的 `budget_src` 和 `location_src`，值為 `meta` 或 `element`

## 測試

無測試框架。測試腳本需真實帳號與網路：

```bash
python test_login.py                                          # 測試登入
python test_remember_me.py                                    # 測試持久化 Cookies
python test_identity_structure.py --case-id TK26022420OAXW21 # 測試特定案件的身份提取
python test_identity_structure.py --keywords "Linux" --top 3 # 搜尋後測試前 3 筆
python test_search_accuracy.py                                # 搜尋結果正確性測試
python test_search_accuracy.py --keywords "Linux,Asterisk"    # 帶關鍵字搜尋
python test_search_accuracy.py --json                         # JSON 格式輸出
```

## Lint / Typecheck

此專案無 lint 或 typecheck 設定。