"""
測試腳本：檢查案件頁面的 HTML 結構，特別是身份(接案身份)欄位
NOTE: 檢查『接案身份』是否被正確提取；沒有的話，表示頁面不在已登入狀態，導致接案資訊不完整
"""

import os
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

from scrapling.fetchers import DynamicFetcher, DynamicSession
from config import Config

def analyze_identity_structure(url):
    """分析案件頁面中身份欄位的 HTML 結構"""

    print(f"正在載入案件頁面: {url}")

            # 建立會話
    session_kwargs = {
        'headless': Config.HEADLESS
    }

    # 啟用記住我
    if Config.REMEMBER_ME:
        user_data_dir = f'/tmp/tasker_user_data_{Config.USERNAME}'
        session_kwargs['user_data_dir'] = user_data_dir

    def login_action(page):
        """登入動作"""
        print("執行登入動作...")

        try:
            # 等待登入頁面載入
            page.wait_for_load_state('networkidle', timeout=10000)
            print("  ✓ 登入頁面載入完成")

            # 輸出登入頁面標題
            title = page.title()
            print(f"  頁面標題: {title}")

            # 檢查登入表單是否存在
            mobile_input = page.query_selector('input[name="mobile"]')
            password_input = page.query_selector('input[name="password"]')
            submit_button = page.query_selector('button[type="submit"]')

            print(f"  手機輸入框: {'存在' if mobile_input else '不存在'}")
            print(f"  密碼輸入框: {'存在' if password_input else '不存在'}")
            print(f"  登入按鈕: {'存在' if submit_button else '不存在'}")

            if not mobile_input or not password_input or not submit_button:
                print("  ⚠️ 登入表單元素未找到，可能頁面結構已改變")
                return

            # 填寫手機號碼
            page.fill('input[name="mobile"]', Config.USERNAME)
            print(f"  ✓ 手機號碼已填寫: {Config.USERNAME[:2]}***{Config.USERNAME[-2:]}")

            # 填寫密碼
            page.fill('input[name="password"]', Config.PASSWORD)
            print("  ✓ 密碼已填寫")

            # 處理『記住我』功能
            if Config.REMEMBER_ME:
                try:
                    remember_label = page.query_selector('label:has(.box-remind)')
                    if remember_label:
                        remember_label.click()
                        print("  ✓ 已啟用『記住我』功能")
                    else:
                        print("  ℹ️  無法勾選『記住我』選項")
                except Exception as e:
                    print(f"  ℹ️  勾選『記住我』時發生錯誤: {e}")

            # 點擊登入按鈕
            page.click('button[type="submit"]')
            print("  ✓ 登入按鈕已點擊")

            # 等待頁面跳轉或處理
            import time
            time.sleep(2)

            # 檢查是否跳轉到案件頁面或首頁
            current_url = page.url
            print(f"  當前 URL: {current_url}")

            # 檢查是否有錯誤訊息
            error_elements = page.query_selector_all('[class*="error"], [class*="alert"], [class*="warning"]')
            if error_elements:
                print("  ⚠️ 發現可能的錯誤訊息:")
                for elem in error_elements:
                    text = elem.text_content()
                    if text:
                        print(f"    - {text}")

        except Exception as e:
            print(f"  ❌ 登入動作失敗: {e}")
            import traceback
            traceback.print_exc()

    try:
        with DynamicSession(**session_kwargs) as session:
            # 執行登入
            print(f"正在使用帳號登入: {Config.USERNAME}")
            print(f"是否啟用記住我: {Config.REMEMBER_ME}")
            session.fetch(
                Config.LOGIN_URL,
                headless=Config.HEADLESS,
                page_action=login_action,
                network_idle=True
            )
            print("登入完成")

            # 檢查登入後是否真的成功
            print("\n檢查登入狀態...")

            # 先訪問案件頁面
            login_page = session.fetch(Config.CASES_URL, headless=Config.HEADLESS, network_idle=True)

            # 查找登入後的頁面中是否有「會員代碼」
            all_text = login_page.css('::text').getall()
            member_code_found = False
            logout_found = False
            login_found = False

            for text in all_text:
                if '會員代碼' in text or '會員編號' in text:
                    member_code_found = True
                    print(f"  ✓ 發現『會員代碼』相關文字: '{text}'")
                    break
                if '登出' in text or 'logout' in text.lower():
                    logout_found = True
                    break
                if '登入' in text and '立即' in text:
                    login_found = True

            if member_code_found:
                print("✓ 發現會員代碼，登入成功")
            elif logout_found:
                print("✓ 發現登出按鈕，登入成功")
            elif login_found:
                print("✗ 發現登入按鈕，可能登入失敗")
            else:
                print("✗ 無法判斷登入狀態")

            # 載入案件頁面
            print(f"\n正在載入案件頁面: {url}")
            page = session.fetch(url, headless=Config.HEADLESS, network_idle=True)
            print("案件頁面載入完成")

            # 保存完整 HTML 到檔案以便檢查
            print("\n保存完整 HTML 到檔案...")
            html_content = page.get()
            output_file = "/tmp/tasker_page_analysis.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✓ 完整 HTML 已保存到: {output_file}")
            print(f"  你可以用文字編輯器開啟此檔案，搜尋『接案身份』")

            print("\n" + "=" * 80)
            print("HTML 結構分析報告")
            print("=" * 80)

            # 1. 查找所有 h2 標籤
            print("\n1. 所有 h2 標籤內容:")
            h2_elements = page.css('h2')
            for i, h2 in enumerate(h2_elements, 1):
                h2_text = h2.css('::text').get('').strip()
                print(f"   h2[{i}]: '{h2_text}'")

            # 2. 查找包含「身份」或「接案」的文字
            print("\n2. 查找包含「身份」或「接案」的文字:")
            all_text = page.css('::text').getall()
            for i, text in enumerate(all_text):
                if '身份' in text or '接案' in text:
                    print(f"   文字[{i}]: '{text.strip()}'")

            # 3. 嘗試使用參考文件中的選擇器
            print("\n3. 嘗試參考文件建議的選擇器:")

            # 3.1 [class*="identity"]
            elem = page.css('[class*="identity"]')
            if elem:
                print(f"   ✓ 找到 [class*=\"identity\"] 元素: {elem[0]}")
                text = elem[0].css('::text').get('').strip()
                print(f"     文字內容: '{text}'")
                # 輸出完整的 HTML 和 class 屬性
                html = elem[0].get()
                print(f"     HTML: {html[:200]}")
            else:
                print(f"   ✗ 未找到 [class*=\"identity\"] 元素")

            # 3.2 [class*="role"]
            elem = page.css('[class*="role"]')
            if elem:
                print(f"   ✓ 找到 [class*=\"role\"] 元素: {elem[0]}")
                text = elem[0].css('::text').get('').strip()
                print(f"     文字內容: '{text}'")
                html = elem[0].get()
                print(f"     HTML: {html[:200]}")
            else:
                print(f"   ✗ 未找到 [class*=\"role\"] 元素")

            # 4. 查找所有帶有 class 的元素，檢查是否包含 identity 或 role
            print("\n4. 查找所有包含 'identity' 或 'role' 的 class:")
            all_elements = page.css('[class]')
            found = False
            for elem in all_elements[:20]:  # 只看前 20 個
                class_attr = elem.css('::attr(class)').get('')
                if 'identity' in class_attr.lower() or 'role' in class_attr.lower():
                    found = True
                    text = elem.css('::text').get('').strip()
                    print(f"   class=\"{class_attr}\": '{text}'")
                    html = elem.get()
                    print(f"     HTML: {html[:150]}")
            if not found:
                print("   未找到包含 'identity' 或 'role' 的 class")

            # 5. 查找所有 p 標籤，檢查內容
            print("\n5. 查找所有 p 標籤內容:")
            p_elements = page.css('p')
            for i, p in enumerate(p_elements[:10]):  # 只看前 10 個
                text = p.css('::text').get('').strip()
                if text and len(text) < 50:  # 只顯示短文字
                    print(f"   p[{i}]: '{text}'")

            # 6. 嘗試查找特定的身份資訊模式
            print("\n6. 嘗試提取身份資訊 (根據可能的模式):")

            # 模式 1: 查找包含「身份」的 li 元素
            li_elements = page.css('li')
            for li in li_elements:
                li_text = li.css('::text').get('').strip()
                if '身份' in li_text or 'Identity' in li_text:
                    print(f"   找到包含「身份」的 li:")
                    print(f"     完整文字: '{li_text}'")
                    # 查找 li 下的 p 元素
                    p_elements = li.css('p')
                    for p in p_elements:
                        p_text = p.css('::text').get('').strip()
                        if p_text:
                            print(f"     p 元素內容: '{p_text}'")

            # 模式 2: 查找包含「身份」的 div
            div_elements = page.css('div')
            for div in div_elements:
                div_text = div.css('::text').get('').strip()
                if '身份' in div_text and len(div_text) < 100:
                    print(f"   找到包含「身份」的 div:")
                    print(f"     完整文字: '{div_text}'")

            # 7. 專門測試「接案身份」提取邏輯
            print("\n7. 測試『接案身份』提取邏輯（模擬程式碼）:")

            # 查找包含「接案身份」文字的 h2 元素
            h2_elements = page.css('h2')
            print(f"   共找到 {len(h2_elements)} 個 h2 元素")

            for i, h2 in enumerate(h2_elements, 1):
                h2_text = h2.css('::text').get('').strip()
                print(f"\n   h2[{i}] 文字: '{h2_text}'")

                if '接案身份' in h2_text:
                    print(f"   ✓ 找到包含『接案身份』的 h2")

                    # 找到 h2 元素後，獲取同一個父元素（li）內的 p 元素
                    parent = h2.parent
                    if parent:
                        print(f"   ✓ 找到父元素: {parent}")

                        # 查找父元素內的 p 元素
                        p_elements = parent.css('p')
                        print(f"   父元素內找到 {len(p_elements)} 個 p 元素")

                        if p_elements:
                            identity_text = p_elements[0].css('::text').get('').strip()
                            print(f"   ✓ 第一個 p 元素的文字: '{identity_text}'")

                            if identity_text:
                                print(f"\n   ✅ 成功提取到身份: '{identity_text}'")
                                break

            # 8. 檢查 meta description（其他欄位從這裡提取）
            print("\n8. 檢查 meta description:")
            meta_desc = page.css('meta[name="description"]')
            if meta_desc:
                content = meta_desc[0].css('::attr(content)').get('')
                print(f"   meta description 內容:")
                print(f"   '{content}'")

                # 分析 meta description 結構
                if '｜' in content:
                    parts = content.split('｜')
                    print(f"\n   meta description 分段 ({len(parts)} 段):")
                    for i, part in enumerate(parts, 1):
                        print(f"   [{i}] '{part}'")
            else:
                print("   未找到 meta description")

            # 9. 嘗試直接使用 li 選擇器
            print("\n9. 嘗試使用 li 選擇器查找:")
            li_elements = page.css('li')
            print(f"   共找到 {len(li_elements)} 個 li 元素")

            for i, li in enumerate(li_elements, 1):
                # 獲取 li 的完整文字
                li_text = ' '.join(li.css('::text').getall())
                if '接案身份' in li_text:
                    print(f"\n   li[{i}] 包含『接案身份』:")
                    print(f"   完整文字: '{li_text}'")

                    # 查找 li 內的 h2 和 p
                    h2_in_li = li.css('h2')
                    p_in_li = li.css('p')

                    if h2_in_li:
                        h2_text = h2_in_li[0].css('::text').get('').strip()
                        print(f"   h2 文字: '{h2_text}'")

                    if p_in_li:
                        p_text = p_in_li[0].css('::text').get('').strip()
                        print(f"   p 文字: '{p_text}'")
                    break

            # 10. 檢查是否有非同步載入（等待更長時間）
            print("\n10. 等待 3 秒後再次檢查 h2 元素:")
            import time
            time.sleep(3)

            h2_elements_after = page.css('h2')
            print(f"   等待後找到 {len(h2_elements_after)} 個 h2 元素")

            for i, h2 in enumerate(h2_elements_after, 1):
                h2_text = h2.css('::text').get('').strip()
                if '接案身份' in h2_text:
                    print(f"   ✓ 等待後找到包含『接案身份』的 h2: '{h2_text}'")
                    break

            # 11. 輸出頁面的完整 HTML（僅前 2000 行）
            print("\n11. 頁面 HTML (前 2000 字符):")
            html_content = page.get()
            print(html_content[:2000])

            print("\n" + "=" * 80)
            print("分析完成")
            print("=" * 80)

    except Exception as e:
        print(f"發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 使用一個已知的案件 URL 進行測試
    test_url = "https://www.tasker.com.tw/cases/TK26022420OAXW21"
    analyze_identity_structure(test_url)
