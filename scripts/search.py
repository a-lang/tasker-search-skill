#!/usr/bin/env python3
"""
Tasker 案件搜尋腳本

支援關鍵字搜尋和參數化輸出
"""

import argparse
import sys
import logging
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scraper import TaskerScraper

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description='搜尋 Tasker 案件並輸出到終端機',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  # 搜尋特定關鍵字
  python scripts/search.py --keywords "Linux,Asterisk,Grafana,N8N" --top 5

  # 獲取最新 5 筆案件（不篩選關鍵字）
  python scripts/search.py --top 5

  # 獲取最新 10 筆案件
  python scripts/search.py --top 10
        '''
    )
    
    parser.add_argument(
        '--keywords',
        type=str,
        default='',
        help='搜尋關鍵字，多個關鍵字用逗號分隔（預設: 空字串）'
    )
    
    parser.add_argument(
        '--top',
        type=int,
        default=5,
        help='要返回的案件數量（預設: 5, 範圍: 1-100）'
    )
    
    return parser.parse_args()


def validate_arguments(args):
    """驗證參數"""
    if args.top < 1 or args.top > 100:
        logger.error("--top 參數必須在 1-100 之間")
        return False
    return True


def main():
    """主函數"""
    # 解析參數
    args = parse_arguments()
    
    # 驗證參數
    if not validate_arguments(args):
        sys.exit(1)
    
    # 執行搜尋
    try:
        scraper = TaskerScraper()
        scraper.search_and_output(
            keywords=args.keywords,
            top=args.top
        )
    except Exception as e:
        logger.error(f"搜尋失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
