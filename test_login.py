#!/usr/bin/env python3
"""
登入功能測試腳本
用於測試 Tasker 網站的登入功能
"""

import logging
from scrapling.fetchers import DynamicSession
from config import Config

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_login():
    """測試登入功能"""
    
    print('🧪 Tasker 登入功能測試')
    print('=' * 50)
    print('')
    
    try:
        # 驗證配置
        Config.validate()
        print('✅ 配置驗證通過')
        print(f'   用戶名 (已脫敏): {Config.USERNAME[:2]}***{Config.USERNAME[-2:]}')
        print(f'   記住我: {"啟用" if Config.REMEMBER_ME else "停用"}')
        print('')
        
        # 建立登入動作
        def login_action(page):
            """執行登入動作"""
            print('🔐 執行登入動作...')

            try:
                # 等待登入頁面載入
                page.wait_for_load_state('networkidle', timeout=10000)
                print('   ✓ 登入頁面載入完成')

                # 檢查登入表單是否存在
                mobile_input = page.query_selector('input[name="mobile"]')
                password_input = page.query_selector('input[name="password"]')
                submit_button = page.query_selector('button[type="submit"]')

                if not mobile_input or not password_input or not submit_button:
                    print('   ⚠️ 登入表單元素未找到，可能頁面結構已改變')
                    return

                # 填寫手機號碼
                page.fill('input[name="mobile"]', Config.USERNAME)
                print(f'   ✓ 手機號碼已填寫: {Config.USERNAME[:2]}***{Config.USERNAME[-2:]}')

                # 填寫密碼
                page.fill('input[name="password"]', Config.PASSWORD)
                print('   ✓ 密碼已填寫')

                # 處理『記住我』功能
                if Config.REMEMBER_ME:
                    try:
                        # 點擊包含『記住我』文字的label
                        remember_label = page.query_selector('label:has(.box-remind)')
                        if remember_label:
                            remember_label.click()
                            print('   ✓ 已啟用『記住我』功能')
                    except:
                        print('   ℹ️  無法勾選『記住我』選項，將使用持久化 cookies')
                else:
                    print('   ℹ️  『記住我』功能已停用')

                # 點擊登入按鈕
                page.click('button[type="submit"]')
                print('   ✓ 登入按鈕已點擊')

            except Exception as e:
                print(f'   ❌ 登入動作失敗: {e}')
                raise
        
        print('🌐 啟動瀏覽器會話...')
        print('')
        
        # 建立會話配置
        session_kwargs = {
            'headless': True,
            'network_idle': True
        }
        
        # 如果啟用『記住我』，設置持久化的用戶數據目錄
        if Config.REMEMBER_ME:
            user_data_dir = f'/tmp/tasker_test_user_data_{Config.USERNAME}'
            session_kwargs['user_data_dir'] = user_data_dir
            print(f'📁 已啟用持久化登入 (Cookies 將保存在: {user_data_dir})')
        else:
            print('ℹ️  使用臨時會話，不保存登入狀態')
        print('')
        
        # 使用 DynamicSession 進行登入測試
        with DynamicSession(**session_kwargs) as session:
            print('📍 導航到登入頁面...')
            session.fetch(
                Config.LOGIN_URL,
                page_action=login_action,
                network_idle=True
            )
            print('   ✓ 登入請求已提交')
            print('')
            
            # 等待一下讓頁面處理
            print('⏳ 等待登入處理...')
            import time
            time.sleep(3)
            
            # 嘗試訪問需要登入的頁面來驗證登入是否成功
            print('🔍 驗證登入狀態...')
            try:
                test_page = session.fetch(
                    Config.CASES_URL,
                    headless=True,
                    network_idle=True
                )
                
                print('   ✓ 成功訪問案件頁面')
                print(f'   HTTP 狀態碼: {test_page.status}')
                print(f'   頁面長度: {len(test_page.body)} bytes')
                print('')
                
                # 檢查頁面內容是否包含會員代碼或登出按鈕
                print('   檢查登入狀態...')

                # 使用標準的 CSS 選擇器獲取所有文字
                all_text = test_page.css('::text').getall()

                member_code_found = False
                logout_found = False
                login_found = False

                for text in all_text:
                    if '會員代碼' in text or '會員編號' in text:
                        member_code_found = True
                        # 提取會員代碼
                        if '會員代碼：' in text:
                            member_code = text.split('會員代碼：')[1].strip()
                            print(f'   ✓ 會員代碼: {member_code}')
                        break
                    if '登出' in text or 'logout' in text.lower():
                        logout_found = True
                        break
                    if '登入' in text and '立即' in text:
                        login_found = True
                        break

                if member_code_found:
                    print('✅ 登入成功！檢測到會員代碼')
                elif logout_found:
                    print('✅ 登入成功！檢測到登出按鈕')
                elif login_found:
                    print('⚠️  可能仍在登入頁面，請檢查登入資訊')
                else:
                    print('✅ 登入成功（能夠訪問案件頁面）')
                
                print('')
                print('🎉 登入功能測試通過！')
                return True
                
            except Exception as e:
                print(f'❌ 驗證登入狀態失敗: {e}')
                return False
                
    except Exception as e:
        print(f'❌ 登入測試失敗: {e}')
        logger.error(f'詳細錯誤: {e}', exc_info=True)
        return False

def main():
    """主函數"""
    try:
        success = test_login()
        
        print('')
        print('=' * 50)
        if success:
            print('✅ 測試結果：成功')
            print('💡 可以進入下一階段：數據爬取測試')
            return 0
        else:
            print('❌ 測試結果：失敗')
            print('💡 請檢查登入資訊或聯繫技術支持')
            return 1
            
    except KeyboardInterrupt:
        print('')
        print('⚠️  測試被用戶中斷')
        return 130
    except Exception as e:
        print('')
        print(f'❌ 測試過程發生錯誤: {e}')
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())