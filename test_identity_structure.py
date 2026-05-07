#!/usr/bin/env python3
"""
測試腳本：檢查案件頁面的 HTML 結構，特別是身份(接案身份)欄位

使用方式:
  # 測試特定案件（用案件 ID）
  python test_identity_structure.py --case-id TK26022420OAXW21

  # 測試特定案件（用完整 URL）
  python test_identity_structure.py --url https://www.tasker.com.tw/cases/TK26022420OAXW21

  # 搜尋案件後測試前 N 筆的身份提取
  python test_identity_structure.py --keywords "Linux,Asterisk" --top 3

  # 搜尋所有案件，測試前 5 筆
  python test_identity_structure.py --top 5

NOTE: 檢查『接案身份』是否被正確提取；沒有的話，表示頁面不在已登入狀態，導致接案資訊不完整
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scraper import TaskerScraper
from config import Config


def format_field(value, max_len=60):
    if not value or value == 'N/A':
        return 'N/A'
    if len(value) > max_len:
        return value[:max_len] + '...'
    return value


def analyze_case(scraper, session, url):
    """分析單一案件頁面的結構，並用 scraper 的方法提取各欄位"""

    print(f"\n{'=' * 70}")
    print(f"案件 URL: {url}")
    print(f"{'=' * 70}")

    try:
        page = session.fetch(url, headless=Config.HEADLESS, network_idle=True)
        scraper._dismiss_lightbox(page)
    except Exception as e:
        print(f"❌ 載入案件頁面失敗: {e}")
        return None

    # 用 scraper 的方法提取各欄位
    title_value, _ = scraper.extract_text(page, 'h1')
    budget_value, budget_src = scraper.extract_from_meta(page, '預算')
    location_value, location_src = scraper.extract_from_meta(page, '地點')
    if budget_value == 'N/A':
        budget_value, budget_src = scraper.extract_text(page, '[class*="budget"], [class*="price"], [class*="money"]')
    if location_value == 'N/A':
        location_value, location_src = scraper.extract_text(page, '[class*="location"], [class*="place"], [class*="area"]')
    identity = scraper.extract_identity(page)
    update_time = scraper.extract_update_time(page)
    description = scraper.extract_description(page)
    case_id = scraper.extract_case_id(url)

    print(f"\n  提取結果:")
    print(f"    標題:     {format_field(title_value)}")
    print(f"    案件 ID:  {case_id}")
    print(f"    預算:     {format_field(budget_value)} (來源: {budget_src})")
    print(f"    地點:     {format_field(location_value)} (來源: {location_src})")
    print(f"    身份:     {identity}")
    print(f"    更新時間: {update_time}")
    print(f"    描述:     {format_field(description, 80)}")

    # 身份欄位詳細分析
    print(f"\n  身份欄位分析:")

    # 方法1：li 遍歷
    li_found = False
    li_elements = page.css('li')
    for i, li in enumerate(li_elements, 1):
        li_text = ' '.join(li.css('::text').getall())
        if '接案身份' in li_text:
            p_elements = li.css('p')
            if p_elements:
                identity_parts = p_elements[0].css('::text').getall()
                li_identity = ''.join(identity_parts).strip()
                print(f"    [li 遍歷]    ✓ 找到: '{li_identity}'")
            else:
                print(f"    [li 遍歷]    ✗ 找到 li 但無 p 子元素")
            li_found = True
            break
    if not li_found:
        print(f"    [li 遍歷]    ✗ 未找到包含「接案身份」的 li")

    # 方法2：h2 + parent
    h2_found = False
    try:
        h2_elements = page.css('h2')
        for h2 in h2_elements:
            h2_text_parts = h2.css('::text').getall()
            h2_text = ''.join(h2_text_parts).strip()
            if '接案身份' in h2_text:
                parent = h2.parent
                if parent:
                    p_elements = parent.css('p')
                    if p_elements:
                        identity_parts = p_elements[0].css('::text').getall()
                        h2_identity = ''.join(identity_parts).strip()
                        print(f"    [h2+parent]  ✓ 找到: '{h2_identity}'")
                    else:
                        print(f"    [h2+parent]  ✗ 找到 h2 但 parent 無 p 子元素")
                else:
                    print(f"    [h2+parent]  ✗ 找到 h2 但無 parent")
                h2_found = True
                break
    except Exception as e:
        print(f"    [h2+parent]  ✗ 發生錯誤: {e}")
    if not h2_found:
        print(f"    [h2+parent]  ✗ 未找到包含「接案身份」的 h2")

    # meta description 分析
    print(f"\n  meta description:")
    meta_desc = page.css('meta[name="description"]')
    if meta_desc:
        content = meta_desc[0].css('::attr(content)').get('')
        if content:
            print(f"    {content[:100]}{'...' if len(content) > 100 else ''}")
        else:
            print(f"    (空)")
    else:
        print(f"    未找到 meta description")

    # 結論
    status = '✅' if identity and identity != 'N/A' else '❌'
    print(f"\n  {status} 身份提取結果: {identity}")

    return {
        'url': url,
        'title': title_value,
        'case_id': case_id,
        'identity': identity,
        'identity_ok': identity is not None and identity != 'N/A',
    }


def main():
    parser = argparse.ArgumentParser(
        description='檢查案件頁面的身份欄位提取正確性',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  # 測試特定案件（用案件 ID）
  python test_identity_structure.py --case-id TK26022420OAXW21

  # 測試特定案件（用完整 URL）
  python test_identity_structure.py --url https://www.tasker.com.tw/cases/TK26022420OAXW21

  # 搜尋案件後測試前 N 筆
  python test_identity_structure.py --keywords "Linux,Asterisk" --top 3
        '''
    )
    parser.add_argument('--case-id', type=str, help='案件 ID（如 TK26022420OAXW21）')
    parser.add_argument('--url', type=str, help='案件完整 URL')
    parser.add_argument('--keywords', type=str, default='', help='搜尋關鍵字，多個用逗號分隔')
    parser.add_argument('--top', type=int, default=0, help='搜尋模式下測試前 N 筆案件（需搭配 --keywords）')

    args = parser.parse_args()

    # 決定要測試的案件 URL 列表
    urls_to_test = []

    if args.url:
        urls_to_test = [args.url]
    elif args.case_id:
        case_id = args.case_id.lstrip('#')
        urls_to_test = [f'{Config.BASE_URL}/cases/{case_id}']
    elif args.keywords:
        # 搜尋模式：先用搜尋找出案件，再逐一測試
        top_count = args.top if args.top > 0 else 5
        try:
            Config.validate()
        except ValueError as e:
            print(f"錯誤: {e}")
            return 1

        print(f"搜尋模式: 關鍵字='{args.keywords}', 測試前 {top_count} 筆")
        scraper = TaskerScraper()

        session_kwargs = {'headless': Config.HEADLESS}
        if Config.REMEMBER_ME:
            session_kwargs['user_data_dir'] = f'/tmp/tasker_user_data_{Config.USERNAME}'

        from scrapling.fetchers import DynamicSession

        with DynamicSession(**session_kwargs) as session:
            if not scraper._check_logged_in(session):
                print("未登入，執行登入流程...")
                scraper.perform_login(session)

            case_links = scraper.search_cases(session, args.keywords)
            if not case_links:
                print("沒有找到任何案件")
                return 0

            urls_to_test = case_links[:top_count]
            print(f"找到 {len(case_links)} 筆案件，將測試前 {len(urls_to_test)} 筆")
    else:
        # 沒有任何參數，顯示使用說明
        parser.print_help()
        return 0

    if not urls_to_test:
        print("沒有可測試的案件")
        return 0

    try:
        Config.validate()
    except ValueError as e:
        print(f"錯誤: {e}")
        print("請確認 .env 檔案已正確設定 TASKER_ID 和 TASKER_PASSWORD")
        return 1

    scraper = TaskerScraper()

    session_kwargs = {'headless': Config.HEADLESS}
    if Config.REMEMBER_ME:
        session_kwargs['user_data_dir'] = f'/tmp/tasker_user_data_{Config.USERNAME}'

    from scrapling.fetchers import DynamicSession

    results = []

    with DynamicSession(**session_kwargs) as session:
        if not scraper._check_logged_in(session):
            print("未登入，執行登入流程...")
            scraper.perform_login(session)
        else:
            print("✓ 已登入")

        for url in urls_to_test:
            result = analyze_case(scraper, session, url)
            if result:
                results.append(result)

    # 總結報告
    if results:
        print(f"\n{'=' * 70}")
        print("總結報告")
        print(f"{'=' * 70}")
        print(f"測試案件數: {len(results)}")
        identity_ok = sum(1 for r in results if r['identity_ok'])
        print(f"身份提取成功: {identity_ok}/{len(results)}")

        if identity_ok < len(results):
            print("\n身份提取失敗的案件:")
            for r in results:
                if not r['identity_ok']:
                    print(f"  - {r.get('case_id', 'N/A')}: {r['url']}")

        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())