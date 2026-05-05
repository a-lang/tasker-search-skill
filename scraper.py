import os
import time
import logging
from pathlib import Path
from datetime import datetime
from scrapling.fetchers import DynamicFetcher, DynamicSession
from config import Config

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskerScraper:
    """Tasker 網站爬蟲類"""
    
    def __init__(self):
        self.config = Config
        self.config.validate()
        self.session = None
        
    def perform_login(self, session):
        """執行登入操作"""
        logger.info("開始登入 Tasker...")
        
        # 導航到登入頁面
        login_page = session.fetch(self.config.LOGIN_URL, headless=self.config.HEADLESS)
        
        # 登入邏輯（根據實際網站結構調整）
        def login_action(page):
            try:
                # 填寫手機號碼（新登入頁面使用 mobile 欄位）
                page.fill('input[name="mobile"]', self.config.USERNAME)
                # 填寫密碼
                page.fill('input[name="password"]', self.config.PASSWORD)
                
                # 處理『記住我』功能
                if self.config.REMEMBER_ME:
                    # 點擊包含checkbox的label來勾選記住我
                    try:
                        # 點擊包含『記住我』文字的label
                        remember_label = page.query_selector('label:has(.box-remind)')
                        if remember_label:
                            remember_label.click()
                            logger.info("✓ 已啟用『記住我』功能")
                    except Exception as e:
                        # 如果點擊失敗，通過持久化 cookies 來實現類似效果
                        logger.info("ℹ️  無法勾選『記住我』選項，將使用持久化 cookies")
                else:
                    logger.info("ℹ️  『記住我』功能已停用")
                
                # 點擊登入按鈕
                page.click('button[type="submit"]')
                logger.info("登入表單提交完成")
            except Exception as e:
                logger.error(f"登入過程發生錯誤: {e}")
                raise
        
        # 執行登入動作
        try:
            session.fetch(
                self.config.LOGIN_URL,
                headless=self.config.HEADLESS,
                page_action=login_action,
                network_idle=True
            )
            logger.info("登入操作完成")
        except Exception as e:
            logger.error(f"登入失敗: {e}")
            raise
    
    def search_cases(self, session, keywords):
        """搜尋案件並返回連結列表
        
        Args:
            session: 已登入的 DynamicSession 物件
            keywords (str): 搜尋關鍵字
            
        Returns:
            list: 案件 URL 列表
        """
        logger.info("載入案件頁面...")
        
        # 載入案件頁面
        def load_cases_page(page):
            try:
                # 等待頁面載入
                page.wait_for_load_state('networkidle', timeout=30000)
                logger.info("✓ 案件頁面載入完成")
                
                # 如果有關鍵字，執行搜尋
                if keywords and keywords.strip():
                    # 將逗號和空格都轉換為統一的空格分隔
                    import re
                    search_keywords = re.sub(r'[,\s]+', ' ', keywords).strip()
                    logger.info(f"原始關鍵字: '{keywords}'")
                    logger.info(f"處理後關鍵字: '{search_keywords}'")
                    
                    # 填寫搜尋框
                    search_input = page.query_selector('input[placeholder*="案件"]')
                    if not search_input:
                        logger.error("✗ 找不到搜尋輸入框")
                        return
                    
                    # 填寫關鍵字
                    search_input.fill(search_keywords)
                    
                    # 驗證填寫的值
                    actual_value = search_input.input_value()
                    logger.info(f"✓ 已填寫搜尋關鍵字: '{actual_value}'")
                    
                    # 點擊搜尋按鈕
                    # 注意: 可能需要等待一段時間讓頁面穩定
                    import time
                    time.sleep(1)
                    
                    # 提交表單（按 Enter 鍵）
                    search_input.press('Enter')
                    logger.info("✓ 已提交搜尋")
                    
                    # 等待搜尋結果載入
                    page.wait_for_load_state('networkidle', timeout=30000)
                    logger.info("✓ 搜尋結果載入完成")
                else:
                    logger.info("沒有提供關鍵字，直接獲取最新案件")
                    
            except Exception as e:
                logger.error(f"載入案件頁面時發生錯誤: {e}")
                raise
        
        try:
            page = session.fetch(
                self.config.CASES_URL,
                headless=self.config.HEADLESS,
                page_action=load_cases_page
            )
            
            # 提取案件連結
            case_links = []
            
            # 查找所有案件連結
            # 注意: 需要根據實際頁面結構調整選擇器
            links = page.css('a[href*="/cases/"]')
            logger.info(f"找到 {len(links)} 個可能的案件連結")
            
            for link in links[:100]:  # 限制最多 100 個連結
                href = link.css('::attr(href)').get('')
                if href and href.startswith('/cases/'):
                    full_url = f"{self.config.BASE_URL}{href}"
                    # 過濾掉非案件頁面（如 /cases/top）
                    if full_url not in case_links and not full_url.endswith('/cases/top'):
                        case_links.append(full_url)
            
            logger.info(f"提取到 {len(case_links)} 個唯一案件連結")
            return case_links
            
        except Exception as e:
            logger.error(f"搜尋案件時發生錯誤: {e}")
            return []
    
    def extract_case_details(self, session, case_links):
        """提取案件詳細資訊
        
        Args:
            session: 已登入的 DynamicSession 物件
            case_links (list): 案件 URL 列表
            
        Returns:
            list: 案件資料列表
        """
        logger.info(f"開始提取 {len(case_links)} 個案件的詳細資訊...")
        cases = []
        
        for i, url in enumerate(case_links, 1):
            try:
                logger.info(f"提取案件 {i}/{len(case_links)}: {url}")
                
                # 載入案件頁面
                page = session.fetch(url, headless=self.config.HEADLESS, network_idle=True)
                
                # 提取案件資訊
                case_data = {
                    'title': self.extract_text(page, 'h1'),
                    'case_id': self.extract_case_id(url),
                    'budget': self.extract_from_meta(page, '預算'),
                    'location': self.extract_from_meta(page, '地點'),
                    'identity': self.extract_identity(page),
                    'update_time': self.extract_update_time(page),
                    'description': self.extract_description(page),
                    'link': url
                }
                
                # 如果沒有從 meta 提取到，嘗試從頁面元素提取
                if case_data['budget'] == 'N/A':
                    case_data['budget'] = self.extract_text(page, '[class*="budget"], [class*="price"], [class*="money"]')
                if case_data['location'] == 'N/A':
                    case_data['location'] = self.extract_text(page, '[class*="location"], [class*="place"], [class*="area"]')
                
                # 只保留有標題的案件
                if case_data['title'] and case_data['title'] != 'N/A':
                    cases.append(case_data)
                    logger.info(f"✓ 提取案件 {i}: {case_data['title']}")
                else:
                    logger.warning(f"✗ 案件 {i} 沒有標題，跳過")
                    
            except Exception as e:
                logger.warning(f"✗ 提取案件 {i} 時發生錯誤: {e}")
                continue
        
        logger.info(f"成功提取 {len(cases)} 筆案件")
        return cases
    
    def extract_from_meta(self, page, field):
        """從 meta description 中提取資訊
        
        Args:
            page: 頁面物件
            field (str): 欄位名稱（預算、地點等）
            
        Returns:
            str: 提取的值，如果找不到則返回 'N/A'
        """
        try:
            import re
            # 獲取 meta description
            meta_desc = page.css('meta[name="description"]')
            if meta_desc:
                content = meta_desc[0].css('::attr(content)').get('')
                
                # 按特殊字符分割
                parts = content.split('｜')
                
                # 查找匹配的欄位
                for part in parts:
                    if field in part:
                        # 提取冒號後的值
                        if '：' in part:
                            value = part.split('：', 1)[1].strip()
                            return value
        except Exception:
            pass
        return 'N/A'
    
    def extract_text(self, page, selector):
        """從頁面提取文字
        
        Args:
            page: 頁面物件
            selector (str): CSS 選擇器
            
        Returns:
            str: 提取的文字，如果找不到則返回 'N/A'
        """
        try:
            elem = page.css(selector)
            if elem:
                text = elem[0].css('::text').get('').strip()
                return text if text else 'N/A'
        except Exception:
            pass
        return 'N/A'
    
    def extract_case_id(self, url):
        """從 URL 提取案件 ID
        
        Args:
            url (str): 案件 URL
            
        Returns:
            str: 案件 ID
        """
        try:
            # 從 URL 提取 ID，例如: https://www.tasker.com.tw/cases/12345 -> #12345
            parts = url.rstrip('/').split('/')
            case_id = parts[-1]
            return f"#{case_id}"
        except Exception:
            return 'N/A'
    
    def extract_identity(self, page):
        """提取接案身份
        
        Args:
            page: 頁面物件
            
        Returns:
            str: 接案身份，如果找不到則返回 'N/A'
        """
        try:
            # 查找包含「接案身份」文字的 h2 元素
            h2_elements = page.css('h2')
            for h2 in h2_elements:
                h2_text = h2.css('::text').get('').strip()
                if '接案身份' in h2_text:
                    # 找到 h2 元素後，獲取同一個父元素（li）內的 p 元素
                    parent = h2.parent
                    if parent:
                        # 查找父元素內的 p 元素（接案身份的值）
                        p_elements = parent.css('p')
                        if p_elements:
                            identity_text = p_elements[0].css('::text').get('').strip()
                            if identity_text:
                                return identity_text
                    break
        except Exception:
            pass
        return 'N/A'
    
    def extract_update_time(self, page):
        """提取更新時間
        
        Args:
            page: 頁面物件
            
        Returns:
            str: 更新時間，如果找不到則返回 'N/A'
        """
        try:
            # 查找包含「更新」文字的 span 元素
            spans = page.css('span')
            for span in spans:
                text = span.css('::text').get('').strip()
                if '更新' in text:
                    # 提取時間部分（格式：2026/05/04 更新）
                    import re
                    match = re.search(r'(\d{4}/\d{2}/\d{2})', text)
                    if match:
                        return match.group(1)
        except Exception:
            pass
        return 'N/A'
    
    def extract_description(self, page):
        """提取案件描述（需求說明）
        
        Args:
            page: 頁面物件
            
        Returns:
            str: 提取的描述，如果找不到則返回 'N/A'
        """
        try:
            # 查找「需求說明」標題元素
            titles = page.css('h2.f-title-s')
            description_title = None
            
            for title in titles:
                title_text = title.css('::text').get('').strip()
                if '需求說明' in title_text:
                    description_title = title
                    break
            
            if description_title:
                # 從「需求說明」標題開始，遍歷後續兄弟元素
                siblings = description_title.xpath('following-sibling::*')
                
                for sibling in siblings:
                    # 檢查元素標籤
                    tag = sibling.tag if hasattr(sibling, 'tag') else ''
                    
                    # 如果遇到新的 h2 標題，停止
                    if tag == 'h2':
                        break
                    
                    # 如果遇到段落，提取文字
                    if tag == 'p':
                        text = sibling.css('::text').get('')
                        if text:
                            # 檢查是否為頁面元素
                            if any(keyword in text for keyword in ['查看完整需求', '登入後即可完整查看', '我要提案', '收藏', '客服時間']):
                                break
                            # 檢查是否為聯絡資訊
                            if 'taskergmail@gmail.com' in text or '0987654321' in text or '02-5579-3438' in text:
                                break
                            # 檢查是否為案件編號或預算
                            if text.startswith('案件編號') or text.startswith('$'):
                                continue
                            # 檢查是否為狀態
                            if any(keyword in text for keyword in ['上線中', 'Email已驗證', '總閱覽', '發現資訊有誤', '您可能感興趣']):
                                continue
                            # 添加到描述
                            return text
                
                # 如果沒有找到明確的描述，返回提示
                return "詳情見頁面"
            
            # 如果沒有找到「需求說明」標題，返回提示
            return "詳情見頁面"
                
        except Exception as e:
            logger.warning(f"提取描述時發生錯誤: {e}")
            pass
        return 'N/A'
    
    def sort_cases_by_time(self, cases):
        """按時間排序案件（最新的在前）
        
        Args:
            cases (list): 案件資料列表
            
        Returns:
            list: 排序後的案件列表
        """
        def parse_time(time_str):
            """解析時間字串"""
            try:
                # 嘗試解析各種時間格式
                from datetime import datetime
                # 這裡需要根據實際時間格式調整
                # 簡單的實現：如果無法解析，返回最早的日期
                return datetime.min
            except:
                return datetime.min
        
        # 按時間排序
        sorted_cases = sorted(
            cases,
            key=lambda x: parse_time(x['update_time']),
            reverse=True  # 最新的在前
        )
        
        return sorted_cases
    
    def print_results(self, keywords, cases):
        """輸出搜尋結果到終端機
        
        Args:
            keywords (str): 搜尋關鍵字
            cases (list): 案件資料列表
        """
        from datetime import datetime
        
        # 生成輸出內容
        keywords_display = keywords if keywords and keywords.strip() else '無'
        
        output = f"""# Tasker 案件搜尋結果

**搜尋關鍵字**: {keywords_display}
**搜尋時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**案件總數**: {len(cases)} 筆

---

"""
        
        # 添加每個案件的詳細資訊
        for i, case in enumerate(cases, 1):
            output += f"""## 案件 {i}: {case['title']}

- **案件 ID**: {case['case_id']}
- **預算**: {case['budget']}
- **地點**: {case['location']}
- **身份**: {case['identity']}
- **更新時間**: {case['update_time']}
- **連結**: {case['link']}

**描述**: {case['description']}

---

"""
        
        # 添加總結表格
        output += "## 總結表格\n\n"
        output += "| 編號 | 標題 | 案件 ID | 預算 | 地點 | 身份 | 更新時間 |\n"
        output += "|------|------|---------|------|------|------|----------|\n"
        
        for i, case in enumerate(cases, 1):
            output += f"| {i} | {case['title']} | {case['case_id']} | {case['budget']} | {case['location']} | {case['identity']} | {case['update_time']} |\n"
        
        # 輸出到終端機
        print(output)
    
    def print_no_results(self, keywords):
        """輸出沒有結果的訊息
        
        Args:
            keywords (str): 搜尋關鍵字
        """
        from datetime import datetime
        
        keywords_display = keywords if keywords and keywords.strip() else '無'
        
        output = f"""# Tasker 案件搜尋結果

**搜尋關鍵字**: {keywords_display}
**搜尋時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**案件總數**: 0 筆

---

## 搜尋結果

⚠️ 沒有找到符合條件的案件。

請嘗試：
- 使用不同的關鍵字搜尋
- 減少關鍵字數量
- 檢查關鍵字拼寫
- 不提供關鍵字以查看所有最新案件

---
"""
        
        print(output)
    
    def search_and_output(self, keywords, top=5):
        """執行搜尋並輸出結果到終端機
        
        Args:
            keywords (str): 搜尋關鍵字，多個關鍵字用逗號分隔
            top (int): 要返回的案件數量
        """
        logger.info(f"開始搜尋案件，關鍵字: '{keywords}', 返回前 {top} 筆")
        
        # 創建會話配置
        session_kwargs = {
            'headless': self.config.HEADLESS
        }
        
        # 如果啟用『記住我』，設置持久化的用戶數據目錄
        if self.config.REMEMBER_ME:
            user_data_dir = f'/tmp/tasker_user_data_{self.config.USERNAME}'
            session_kwargs['user_data_dir'] = user_data_dir
            logger.info(f"✓ 已啟用持久化登入 (Cookies 將保存在: {user_data_dir})")
        else:
            logger.info("ℹ️  使用臨時會話，不保存登入狀態")
        
        # 使用 with 語句管理 session 生命週期
        with DynamicSession(**session_kwargs) as session:
            # 執行登入
            self.perform_login(session)
            
            # 搜尋案件
            case_links = self.search_cases(session, keywords)
            
            if not case_links:
                logger.info("沒有找到任何案件")
                self.print_no_results(keywords)
                return
            
            # 提取案件詳情
            cases = self.extract_case_details(session, case_links)
            
            if not cases:
                logger.info("沒有提取到任何案件詳情")
                self.print_no_results(keywords)
                return
            
            # 排序並選擇前 N 筆
            sorted_cases = self.sort_cases_by_time(cases)
            top_cases = sorted_cases[:top]
            
            # 輸出到終端機
            self.print_results(keywords, top_cases)


def main():
    """主函數"""
    try:
        scraper = TaskerScraper()
        scraper.run()
    except Exception as e:
        logger.error(f"程式執行失敗: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())