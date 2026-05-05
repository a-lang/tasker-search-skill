#!/usr/bin/env python3
"""
詳細的登入狀態分析腳本
"""

import logging
from scrapling.fetchers import DynamicFetcher, DynamicSession
from config import Config

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def analyze_login_page():
    """分析登入前後的頁面狀態"""
    
    print('🔍 Tasker 登入狀態詳細分析')
    print('=' * 60)
    print('')
    
    try:
        Config.validate()
        
        # 第一步：獲取未登入的案件頁面作為對比
        print('📊 步驟1：獲取未登入的案件頁面（對比基準）')
        print('-' * 60)
        
        unauth_page = DynamicFetcher.fetch(
            Config.CASES_URL,
            headless=True,
            network_idle=True
        )
        
        print(f'✅ 獲取成功 (HTTP {unauth_page.status})')
        print(f'   頁面長度: {len(unauth_page.body)} bytes')
        
        # 檢查未登入頁面的特徵
        unauth_features = extract_page_features(unauth_page)
        print(f'   主要按鈕: {", ".join(unauth_features["buttons"])}')
        print(f'   主要連結: {", ".join(unauth_features["links"][:5])}')
        print('')
        
        # 第二步：執行登入並獲取登入後的頁面
        print('📊 步驟2：登入後的案件頁面')
        print('-' * 60)
        
        with DynamicSession(headless=True, network_idle=True) as session:
            # 執行登入
            def login_action(page):
                page.fill('input[name="account"]', Config.USERNAME)
                page.fill('input[name="password"]', Config.PASSWORD)
                page.click('button[type="submit"]')
            
            session.fetch(Config.LOGIN_URL, page_action=login_action)
            print('✅ 登入動作已執行')
            
            # 等待登入處理
            import time
            time.sleep(3)
            
            # 獲取登入後的頁面
            auth_page = session.fetch(Config.CASES_URL, headless=True, network_idle=True)
            
            print(f'✅ 獲取成功 (HTTP {auth_page.status})')
            print(f'   頁面長度: {len(auth_page.body)} bytes')
            
            # 檢查登入後頁面的特徵
            auth_features = extract_page_features(auth_page)
            print(f'   主要按鈕: {", ".join(auth_features["buttons"])}')
            print(f'   主要連結: {", ".join(auth_features["links"][:5])}')
            print('')
        
        # 第三步：對比分析
        print('📊 步驟3：對比分析')
        print('-' * 60)
        
        page_length_diff = abs(len(auth_page.body) - len(unauth_page.body))
        print(f'頁面長度差異: {page_length_diff} bytes')
        
        if len(auth_page.body) > len(unauth_page.body):
            print('✅ 登入後頁面內容更多（可能包含個人化內容）')
        elif len(auth_page.body) < len(unauth_page.body):
            print('⚠️  登入後頁面內容更少（可能被重定向）')
        else:
            print('ℹ️  登入前後頁面內容相同')
        
        print('')
        
        # 檢查按鈕變化
        print('按鈕對比：')
        unauth_buttons = set(unauth_features["buttons"])
        auth_buttons = set(auth_features["buttons"])
        
        if unauth_buttons != auth_buttons:
            new_buttons = auth_buttons - unauth_buttons
            removed_buttons = unauth_buttons - auth_buttons
            
            if new_buttons:
                print(f'  ➕ 新增按鈕: {", ".join(new_buttons)}')
            if removed_buttons:
                print(f'  ➖ 移除按鈕: {", ".join(removed_buttons)}')
            
            if '登出' in new_buttons or '登出' in auth_buttons:
                print('  ✅ 檢測到登出按鈕 -> 登入成功！')
            elif '登入' in auth_buttons:
                print('  ⚠️  仍有登入按鈕 -> 登入可能失敗')
        else:
            print('  ℹ️  按鈕無變化')
        
        print('')
        
        # 檢查連結變化
        print('連結對比：')
        unauth_links = set(unauth_features["links"])
        auth_links = set(auth_features["links"])
        
        new_links = auth_links - unauth_links
        if new_links:
            print(f'  ➕ 新增連結數量: {len(new_links)}')
            if any('/users/' in link for link in new_links):
                print('  ✅ 檢測到用戶相關連結 -> 登入可能成功！')
        
        print('')
        
        # 保存頁面內容供人工檢查
        save_pages_for_inspection(unauth_page, auth_page)
        
        print('=' * 60)
        print('🎯 分析完成！請查看上面的結果判斷登入狀態')
        print('💡 頁面內容已保存至 /tmp/tasker_pages/ 目錄供人工檢查')
        
    except Exception as e:
        print(f'❌ 分析失敗: {e}')
        logger.error('詳細錯誤', exc_info=True)
        return False
    
    return True

def extract_page_features(page):
    """從頁面提取特徵"""
    features = {
        'buttons': [],
        'links': []
    }
    
    # 提取按鈕文字
    buttons = page.css('button, a[role="button"]')
    for btn in buttons:
        btn_text = btn.text.strip()
        if btn_text and len(btn_text) < 20:  # 過濾太長的文字
            features['buttons'].append(btn_text)
    
    # 提取主要連結
    links = page.css('a')
    for link in links:
        href = link.css('::attr(href)').get('')
        link_text = link.text.strip()
        if href and link_text and len(link_text) < 30:
            features['links'].append(link_text)
    
    return features

def save_pages_for_inspection(unauth_page, auth_page):
    """保存頁面內容供人工檢查"""
    import os
    os.makedirs('/tmp/tasker_pages', exist_ok=True)
    
    with open('/tmp/tasker_pages/unauth_cases.html', 'w', encoding='utf-8') as f:
        f.write(unauth_page.body.decode('utf-8', errors='ignore'))
    
    with open('/tmp/tasker_pages/auth_cases.html', 'w', encoding='utf-8') as f:
        f.write(auth_page.body.decode('utf-8', errors='ignore'))
    
    print('💾 頁面內容已保存:')
    print('   - /tmp/tasker_pages/unauth_cases.html (未登入)')
    print('   - /tmp/tasker_pages/auth_cases.html (登入後)')

if __name__ == "__main__":
    analyze_login_page()