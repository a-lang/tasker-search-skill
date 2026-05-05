# Tasker 案件搜尋 Skill

符合 Agent Skills 標準的 Tasker 案件搜尋工具，讓 AI Agent 能夠搜尋 tasker.com.tw 上的「我要接案」案件。

## 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
playwright install chromium
```

### 配置

複製 `.env.example` 到 `.env` 並填寫您的登入資訊。

### 使用

```bash
# 搜尋特定關鍵字
python scripts/search.py --keywords "Linux,Asterisk" --top 5

# 獲取最新案件
python scripts/search.py --top 5
```

## Skill 使用

此專案符合 [Agent Skills 規範](https://agentskills.io/)，可被 AI Agent 調用。

詳見 [SKILL.md](SKILL.md)。

## 文檔

- [SKILL.md](SKILL.md) - Skill 定義
- [設計文件](docs/superpowers/specs/2026-05-04-tasker-case-search-design.md) - 完整設計
- [技術參考](references/REFERENCE.md) - 技術參考
- [技術細節](references/TECHNICAL.md) - 技術細節

---

# Tasker 爬蟲專案（舊版）

這是一個使用 Scrapling 框架開發的自動化爬蟲，用於抓取 Tasker (出任務) 網站的案件數據。

## 功能特點

- ✅ 自動化登入功能（手機號碼/身分證字號登入）
- ✅ **『記住我』功能**（持久化登入狀態，無需重複登入）
- ✅ 案件列表數據抓取
- ✅ Markdown 格式輸出
- ✅ Headless 瀏覽器模式
- ✅ 錯誤處理和日誌記錄
- ✅ 環境變數配置

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 配置說明

1. **複製並編輯環境變數文件**：
   ```bash
   # 編輯 .env 文件，填寫您的登入資訊
   TASKER_ID=your_id_number_here
   TASKER_PASSWORD=your_password_here
   ```

2. **重要配置項**：
   - `TASKER_ID`: 您的身分證字號或統一編號
   - `TASKER_PASSWORD`: 您的登入密碼
   - `HEADLESS_MODE`: 是否使用無頭瀏覽器（true/false）
   - `REMEMBER_ME`: 是否啟用『記住我』功能（true/false），預設為 true
   - `MAX_PAGES`: 最大爬取頁數
   - `SCRAPER_DELAY`: 請求延遲時間（秒）

3. **關於『記住我』功能**：
   - 預設啟用，會將登入 cookies 保存在系統臨時目錄
   - 通過點擊登入頁面的「記住我」選項來啟用
   - 啟用後後續執行時無需重新登入
   - 持久化數據保存在 `/tmp/tasker_user_data_[用戶名]` 目錄

## 使用方法

### 基本使用

```bash
python scraper.py
```

### 運行後

- 爬蟲會自動登入 Tasker 網站
- 抓取案件列表數據
- 將結果保存為 Markdown 格式
- 輸出文件位於 `output/` 目錄

## 輸出格式

輸出文件為 Markdown 格式，包含以下信息：

```markdown
# Tasker 案件數據報告

**生成時間**: 2026-05-04 15:00:00  
**案件總數**: X 筆

## 案件列表

### 案件 1

**標題**: 案件標題

- **金額**: $X
- **地點**: 地點
- **時間**: 時間
- **網址**: 案件網址

**描述**: 案件描述

**標籤**: 標籤1, 標籤2
```

## 項目結構

```
tasker-search-skill/
├── .env              # 環境變數配置（不提交到版本控制）
├── .gitignore        # Git 忽略文件
├── config.py         # 配置管理
├── scraper.py        # 主要爬蟲程式
├── requirements.txt  # Python 依賴
├── output/          # 輸出目錄
│   └── cases_data_YYYYMMDD_HHMMSS.md
└── README.md        # 本文件
```

## 注意事項

### 安全性
- ⚠️ **切勿**將 `.env` 文件提交到版本控制
- ⚠️ 保護您的登入資訊，不要分享給他人
- ✅ `.gitignore` 已配置忽略敏感文件

### 使用限制
- 請遵守 Tasker 網站的使用條款
- 適當設置爬取延遲，避免對網站造成壓力
- 尊重網站的 robots.txt 規定

### 開發狀態
- 🟢 **第1項**：✅ 瀏覽器依賴安裝完成
- 🟢 **第2項**：✅ 專案結構建立完成
- 🟢 **選項1**：✅ 登入功能測試完成
- 🟢 **新增功能**：✅ 『記住我』功能已實現並測試
- 🟢 **功能優化**：✅ 使用正確的登入頁面
- 🟡 **第3項**：數據爬取模組開發中
- ⚪ **第4項**：輸出與格式化開發中

## 故障排除

### 常見問題

### 關於『記住我』功能

1. **功能說明**：
   - 預設啟用，會將登入 cookies 保存在系統臨時目錄
   - 啟用後後續執行時無需重新登入，提高效率
   - 持久化數據保存在 `/tmp/tasker_user_data_[用戶名]` 目錄

2. **清除登入狀態**：
   ```bash
   # 方法1：停用記住我功能
   # 編輯 .env 文件，設置：
   REMEMBER_ME=false
   
   # 方法2：手動刪除持久化數據
   rm -rf /tmp/tasker_user_data_[您的用戶名]
   ```

3. **測試記住我功能**：
   ```bash
   python test_remember_me.py
   ```

### 登入問題

1. **登入失敗**
   - 檢查 `.env` 文件中的登入資訊是否正確
   - 確認網絡連接正常
   - 查看日誌輸出了解具體錯誤

2. **抓取不到數據**
   - 檢查網站結構是否有變化
   - 嘗試調整 CSS 選擇器
   - 增加延遲時間

3. **瀏覽器問題**
   - 運行 `scrapling install` 重新安裝瀏覽器依賴
   - 檢查系統依賴是否完整

## 技術棧

- **Python**: 3.10+
- **Scrapling**: 0.4.7
- **Playwright**: 瀏覽器自動化引擎
- **python-dotenv**: 環境變數管理

## 授權聲明

本項目僅供學習和研究使用。使用者需自行負責確保遵守目標網站的使用條款和相關法律法規。

## 支持與貢獻

如有問題或建議，請通過以下方式聯繫：
- 創建 Issue
- 發送 Pull Request

---

**生成時間**: 2026-05-04  
**版本**: 1.0.0-alpha