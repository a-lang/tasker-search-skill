import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Config:
    """爬蟲配置類"""
    
    # Tasker 網站配置
    BASE_URL = 'https://www.tasker.com.tw'
    LOGIN_URL = f'{BASE_URL}/auth/login'  # 使用手機版登入頁面
    CASES_URL = f'{BASE_URL}/cases'
    
    # 登入資訊
    USERNAME = os.getenv('TASKER_ID', '')
    PASSWORD = os.getenv('TASKER_PASSWORD', '')
    
    # 爬蟲行為配置
    DELAY = int(os.getenv('SCRAPER_DELAY', 2))
    MAX_PAGES = int(os.getenv('MAX_PAGES', 10))
    HEADLESS = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
    REMEMBER_ME = os.getenv('REMEMBER_ME', 'true').lower() == 'true'
    
    # 輸出配置
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
    OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'cases_data.md')
    
    @classmethod
    def validate(cls):
        """驗證必要配置"""
        if not cls.USERNAME or not cls.PASSWORD:
            raise ValueError("請在 .env 文件中設置 TASKER_ID 和 TASKER_PASSWORD")
        return True