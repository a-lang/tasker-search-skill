#!/usr/bin/env python3
"""
測試『記住我』功能
驗證登入狀態的持久化功能
"""

import os
import logging
from scrapling.fetchers import DynamicSession
from config import Config

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_remember_me():
    """測試『記住我』功能"""
    
    print('🧪 Tasker 『記住我』功能測試')
    print('=' * 60)
    print('')
    
    try:
        # 驗證配置
        Config.validate()
        
        # 檢查是否啟用記住我
        if not Config.REMEMBER_ME:
            print('❌ 『記住我』功能未啟用')
            print('   請在 .env 文件中設置 REMEMBER_ME=true')
            return False
        
        print('✅ 配置驗證通過')
        print(f'   用戶名 (已脫敏): {Config.USERNAME[:2]}***{Config.USERNAME[-2:]}')
        print(f'   記住我: 啟用')
        print('')
        
        # 檢查是否存在持久化數據
        user_data_dir = f'/tmp/tasker_user_data_{Config.USERNAME}'
        session_data_exists = os.path.exists(user_data_dir)
        
        print('📁 檢查持久化數據:')
        if session_data_exists:
            print(f'   ✓ 找到持久化數據目錄: {user_data_dir}')
        else:
            print(f'   ✗ 未找到持久化數據目錄: {user_data_dir}')
            print('   這將進行首次登入並建立持久化數據')
        print('')
        
        # 測試登入流程
        def login_action(page):
            """執行登入動作"""
            try:
                # 填寫手機號碼
                page.fill('input[name="mobile"]', Config.USERNAME)
                # 填寫密碼
                page.fill('input[name="password"]', Config.PASSWORD)
                
                # 處理『記住我』功能
                if Config.REMEMBER_ME:
                    try:
                        # 點擊包含『記住我』文字的label
                        remember_label = page.query_selector('label:has(.box-remind)')
                        if remember_label:
                            remember_label.click()
                    except Exception as e:
                        # 如果點擊失敗，通過持久化 cookies 來實現類似效果
                        logger.info("無法勾選『記住我』選項，將使用持久化 cookies")
                
                # 點擊登入按鈕
                page.click('button[type="submit"]')
            except Exception as e:
                logger.error(f"登入動作失敗: {e}")
                raise
        
        print('🌐 啟動瀏覽器會話（使用持久化 cookies）...')
        session_kwargs = {
            'headless': True,
            'network_idle': True,
            'user_data_dir': user_data_dir
        }
        
        with DynamicSession(**session_kwargs) as session:
            # 嘗試直接訪問需要登入的頁面
            print('📍 嘗試訪問需要登入的頁面...')
            test_page = session.fetch(
                Config.CASES_URL,
                headless=True,
                network_idle=True
            )
            
            # 檢查登入狀態
            print('   檢查登入狀態...')
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
                print('✅ 使用持久化 cookies 登入成功！')
                print('   『記住我』功能正常運作')
            elif logout_found:
                print('✅ 使用持久化 cookies 登入成功！')
                print('   『記住我』功能正常運作')
            elif login_found:
                print('⚠️  需要重新登入，執行登入流程...')

                # 執行登入
                session.fetch(
                    Config.LOGIN_URL,
                    page_action=login_action,
                    network_idle=True
                )
                print('   ✓ 登入流程執行完成')

                # 再次嘗試訪問
                import time
                time.sleep(2)
                test_page = session.fetch(
                    Config.CASES_URL,
                    headless=True,
                    network_idle=True
                )

                all_text = test_page.css('::text').getall()
                member_code_found = False

                for text in all_text:
                    if '會員代碼' in text or '會員編號' in text:
                        member_code_found = True
                        break

                if member_code_found:
                    print('✅ 登入成功！cookies 已持久化保存')
                else:
                    print('❌ 登入失敗')
                    return False
            else:
                print('ℹ️  登入狀態不明確')
            
            print('')
            
                # 檢查持久化數據是否被建立
            if os.path.exists(user_data_dir):
                print(f'✅ 持久化數據已保存: {user_data_dir}')
                print(f'   下次執行時將自動使用這些 cookies')
            else:
                print('⚠️  持久化數據目錄未找到，可能配置有誤')
        
        print('')
        print('=' * 60)
        print('🎉 『記住我』功能測試完成！')
        print('💡 下次執行時，系統將自動使用保存的登入狀態')
        return True
        
    except Exception as e:
        print(f'❌ 測試失敗: {e}')
        logger.error('詳細錯誤', exc_info=True)
        return False

def main():
    """主函數"""
    try:
        success = test_remember_me()
        
        print('')
        if success:
            return 0
        else:
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