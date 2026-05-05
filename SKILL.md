---
name: tasker-case-search
description: Searches for cases on tasker.com.tw with keyword filtering, returns sorted results in Markdown format. Use when user requests to search for Tasker cases, find freelance opportunities, or look for specific project types.
license: MIT
compatibility: Requires Python 3.10+, network access to tasker.com.tw, and Scrapling framework
metadata:
  author: opencode
  version: "1.0"
  language: zh-TW
---

# Tasker 案件搜尋

這個技能允許搜尋 tasker.com.tw 上的「我要接案」案件，並返回排序後的案件資訊。

## 功能

- 根據關鍵字搜尋 Tasker 案件
- 按時間新至舊排序
- 返回前 N 筆案件的詳細資訊
- 以 Markdown 格式輸出結果

## 什麼時候使用

當用戶請求以下內容時使用此技能：
- 搜尋 Tasker 案件
- 查找特定技術的專案機會
- 尋找自由接案工作
- 獲取特定類型的案件資訊

## 使用方法

1. 確定搜尋關鍵字（多個關鍵字用逗號分隔，可選）
2. 確定要返回的案件數量（預設 5 筆）
3. 執行搜尋腳本

### 命令列範例

```bash
# 搜尋特定關鍵字
python scripts/search.py --keywords "Linux,Asterisk,Grafana,N8N" --top 5

# 獲取最新 5 筆案件（不篩選關鍵字）
python scripts/search.py --top 5

# 獲取最新 10 筆案件
python scripts/search.py --top 10
```

## 輸入參數

- `keywords` (string, optional): 搜尋關鍵字，多個關鍵字用逗號分隔
  - 預設: 空字串（不進行關鍵字篩選）
  - 範例: "Linux,Asterisk,Grafana,N8N"
  - 注意: 多個關鍵字會合併為單一搜尋字串

- `top` (integer, optional): 要返回的案件數量
  - 預設: 5
  - 範例: 5
  - 範圍: 1-100

## 輸出格式

返回 Markdown 格式的搜尋結果，包含：

### 1. 搜尋摘要
- 搜尋關鍵字
- 搜尋時間
- 案件總數

### 2. 案件詳細資訊
每個案件包含：
- 標題 (title)
- 案件 ID (case_id)
- 預算 (budget)
- 地點 (location)
- 身份 (identity)
- 更新時間 (update_time)
- 描述 (description)
- 連結 (link)

### 3. 總結表格
所有案件的快速概覽，按新至舊排列

## 輸出範例

```markdown
# Tasker 案件搜尋結果

**搜尋關鍵字**: Linux, Asterisk, Grafana, N8N
**搜尋時間**: 2026-05-04 16:30:00
**案件總數**: 3 筆

---

## 案件 1: Linux 伺服器維護

- **案件 ID**: #12345
- **預算**: $50,000
- **地點**: 台北市
- **身份**: 公司
- **更新時間**: 2026-05-04 14:30
- **連結**: https://www.tasker.com.tw/cases/12345

**描述**: 尋找有 Linux 伺服器維護經驗的工程師...

---

## 總結表格

| 編號 | 標題 | 案件 ID | 預算 | 地點 | 身份 | 更新時間 |
|------|------|---------|------|------|------|----------|
| 1 | Linux 伺服器維護 | #12345 | $50,000 | 台北市 | 公司 | 2026-05-04 |
...
```

## 錯誤處理

如果搜尋失敗或沒有結果，技能會返回明確的錯誤訊息：

- **沒有搜尋結果**: 顯示提示訊息，建議用戶調整關鍵字
- **網路錯誤**: 記錄錯誤並終止
- **頁面載入失敗**: 記錄警告並跳過該頁面

## 依賴要求

- 必須先登入 tasker.com.tw
- 使用「記住我」功能避免重複登入
- 需要 Python 3.10+ 環境
- 需要 Scrapling 0.4.7 框架

## 技術細節

搜尋流程：
1. 登入（使用記住我功能）
2. 填寫搜尋關鍵字（如果提供）
3. 點擊搜尋按鈕（如果提供關鍵字）
4. 從搜尋結果頁面提取案件連結
5. 逐一訪問案件詳細頁面
6. 提取完整的案件資訊
7. 按時間排序並選擇前 N 筆
8. 格式化並輸出 Markdown

## 參考資源

- 參考文件: `references/REFERENCE.md`
- 技術細節: `references/TECHNICAL.md`
