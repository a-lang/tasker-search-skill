#!/usr/bin/env python3
"""
搜尋結果正確性測試

依頁面原始順序列出所有案件資訊，方便使用者在 Chrome 上手動比對。

使用方式:
  python test_search_accuracy.py --keywords "Linux,Asterisk"
  python test_search_accuracy.py  # 不篩選關鍵字，列出所有案件
"""

import argparse
import json
import sys
import logging
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scraper import TaskerScraper
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='搜尋結果正確性測試 — 依頁面原始順序列出所有案件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  python test_search_accuracy.py --keywords "Linux,Asterisk"
  python test_search_accuracy.py
        '''
    )
    parser.add_argument(
        '--keywords',
        type=str,
        default='',
        help='搜尋關鍵字，多個關鍵字用逗號分隔'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='以 JSON 格式輸出（方便程式比對）'
    )
    return parser.parse_args()


def run_search(keywords):
    """執行搜尋並回傳案件列表（原始順序，不排序）"""
    scraper = TaskerScraper()

    session_kwargs = {'headless': Config.HEADLESS}
    if Config.REMEMBER_ME:
        session_kwargs['user_data_dir'] = f'/tmp/tasker_user_data_{Config.USERNAME}'

    from scrapling.fetchers import DynamicSession

    with DynamicSession(**session_kwargs) as session:
        if not scraper._check_logged_in(session):
            logger.info("未登入，執行登入流程...")
            scraper.perform_login(session)
        else:
            logger.info("✓ 已登入，跳過登入流程")

        case_links = scraper.search_cases(session, keywords)

        if not case_links:
            return []

        cases = scraper.extract_case_details(session, case_links)
        return cases


def format_human(cases, keywords):
    """人類可讀格式"""
    keywords_display = keywords if keywords and keywords.strip() else '無'

    lines = []
    lines.append("=" * 70)
    lines.append("搜尋結果（原始順序）")
    lines.append("=" * 70)
    lines.append(f"關鍵字: {keywords_display}")
    lines.append(f"頁面案件數: {len(cases)}")
    lines.append("")

    for i, case in enumerate(cases, 1):
        title = case.get('title', '[無標題]') or '[無標題]'
        lines.append(f"{i}. {title}")
        lines.append(f"   ID: {case.get('case_id', 'N/A')}")
        lines.append(f"   預算: {case.get('budget', 'N/A')} (來源: {case.get('budget_src', 'N/A')})")
        lines.append(f"   地點: {case.get('location', 'N/A')} (來源: {case.get('location_src', 'N/A')})")
        lines.append(f"   身份: {case.get('identity', 'N/A')}")
        lines.append(f"   更新時間: {case.get('update_time', 'N/A')}")
        desc = case.get('description', 'N/A') or 'N/A'
        if len(desc) > 100:
            desc = desc[:100] + '...'
        lines.append(f"   描述: {desc}")
        lines.append(f"   連結: {case.get('link', 'N/A')}")
        lines.append("")

    lines.append("=" * 70)
    lines.append("比對說明: 請在 Chrome 開啟同一搜尋頁面，逐筆核對上述資訊")
    lines.append("=" * 70)

    return '\n'.join(lines)


def format_json(cases, keywords):
    """JSON 格式"""
    output = []
    for case in cases:
        output.append({
            'title': case.get('title') or '[無標題]',
            'case_id': case.get('case_id', 'N/A'),
            'budget': case.get('budget', 'N/A'),
            'budget_src': case.get('budget_src', 'N/A'),
            'location': case.get('location', 'N/A'),
            'location_src': case.get('location_src', 'N/A'),
            'identity': case.get('identity', 'N/A'),
            'update_time': case.get('update_time', 'N/A'),
            'description': case.get('description', 'N/A'),
            'link': case.get('link', 'N/A'),
        })
    return json.dumps(output, ensure_ascii=False, indent=2)


def main():
    args = parse_arguments()

    try:
        Config.validate()
    except ValueError as e:
        print(f"錯誤: {e}")
        print("請確認 .env 檔案已正確設定 TASKER_ID 和 TASKER_PASSWORD")
        return 1

    try:
        cases = run_search(args.keywords)

        if not cases:
            keywords_display = args.keywords if args.keywords and args.keywords.strip() else '無'
            print(f"沒有找到任何案件（關鍵字: {keywords_display}）")
            return 0

        if args.json:
            print(format_json(cases, args.keywords))
        else:
            print(format_human(cases, args.keywords))

    except Exception as e:
        logger.error(f"搜尋失敗: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())