# Tasker 案件搜尋 - 技術參考

## 概述

本文件提供 Tasker 案件搜尋 skill 的技術參考資訊。

## 模組說明

### scraper.py

主要的爬蟲模組，包含以下功能：

#### TaskerScraper 類

主要方法：
- `create_session()`: 建立已登入的會話
- `perform_login(session)`: 執行登入操作
- `search_and_output(keywords, top)`: 執行搜尋並輸出結果
- `search_cases(session, keywords)`: 搜尋案件並返回連結
- `extract_case_details(session, case_links)`: 提取案件詳細資訊
- `sort_cases_by_time(cases)`: 按時間排序案件
- `print_results(keywords, cases)`: 輸出搜尋結果
- `print_no_results(keywords)`: 輸出沒有結果的訊息

### config.py

配置模組，包含以下配置：

- `BASE_URL`: Tasker 基礎 URL
- `LOGIN_URL`: 登入頁面 URL
- `CASES_URL`: 案件頁面 URL
- `TASKER_ID`: 用戶名稱
- `TASKER_PASSWORD`: 密碼
- `REMEMBER_ME`: 是否啟用記住我功能
- `HEADLESS`: 是否使用無頭模式

### scripts/search.py

命令列介面腳本：

參數：
- `--keywords`: 搜尋關鍵字
- `--top`: 返回案件數量

## CSS 選擇器參考

### 登入頁面
- 手機號碼輸入框: `input[name="mobile"]`
- 密碼輸入框: `input[name="password"]`
- 記住我功能: `label:has(.box-remind)`
- Lightbox 彈窗: `.box-lightbox`（所有頁面互動前必須先關閉）

### 案件頁面
- 搜尋輸入框: `input[placeholder*="案件"]`（備用: `input[type="search"]`, `input[name="keyword"]`）
- 搜尋按鈕: `button[type="submit"], button[class*="search"]`（fallback: 按 Enter 鍵）
- 案件連結: 用正則 `/cases/TK[A-Za-z0-9]+` 過濾

### 案件詳細頁面
- 標題: `h1, .case-title, [class*="title"]`
- 預算: `[class*="budget"], [class*="price"], [class*="money"]`
- 地點: `[class*="location"], [class*="place"], [class*="area"]`
- 身份: `[class*="identity"], [class*="role"]`
- 時間: `[class*="time"], [class*="date"], time`
- 描述: `[class*="description"], [class*="detail"], p`

## 持久化數據

### 路徑
`/tmp/tasker_user_data_[username]`

### 內容
- Cookies
- 瀏覽器會話數據

### 清理
```bash
rm -rf /tmp/tasker_user_data_[username]
```

## 常見問題

### Q: 搜尋失敗怎麼辦？
A: 檢查網路連線、確認登入狀態、查看日誌輸出。

### Q: 如何調整提取問題？
A: 增加 logging 級別到 DEBUG：`logging.basicConfig(level=logging.DEBUG)`

### Q: 如何清理登入狀態？
A: 刪除持久化數據目錄：`rm -rf /tmp/tasker_user_data_*`

## 相關文件
- [TECHNICAL.md](TECHNICAL.md) - 技術細節
- [SKILL.md](../SKILL.md) - Skill 定義
