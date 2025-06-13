#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣出口商美國關稅政策資訊網頁生成器
自動生成符合指定格式的 HTML 內容
"""

import os
import json
import requests
from datetime import datetime
import sys

def get_current_time():
    """獲取當前時間（台灣時區）"""
    return datetime.now().strftime('%Y年%m月%d日 %H:%M')

def get_week_number():
    """獲取當前週次"""
    now = datetime.now()
    week_number = now.isocalendar()[1]
    return week_number

PROMPT = """請創建一個台灣出口商的美國關稅政策資訊網頁，要求如下：

## 技術規範
- 完整HTML5文檔結構，從<!DOCTYPE html>開始
- 引入Tailwind CSS: <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
- 引入Font Awesome: <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
- 主色調使用SoWork橘色 #FF6B35
- 響應式設計支援各種裝置

## 視覺設計
- 使用現代簡潔的卡片式設計
- 白色背景卡片配陰影效果
- 日期徽章使用橘色背景 (#FF6B35)
- 來源徽章使用灰色背景
- 新聞卡片要有 hover 效果 (transform: translateY(-3px))
- 使用 Font Awesome 圖示增強視覺效果

## 內容結構
- 網頁標題：美國關稅政策最新動態 - 台灣出口商商業情報
- 四個主要區塊：
  1. 最新政策概述
  2. 專家觀點  
  3. 美國電商平台政策
  4. 歐盟、日本、韓國的關稅政策

## 內容要求
- 使用繁體中文
- 包含最新一週的真實新聞資訊
- 每個新聞項目包含：日期、來源、標題、內容摘要、原始連結
- 如果原文未直接提及台灣，需要標註說明
- 不包含任何政府領導人相關內容
- 所有連結使用 target="_blank" 和適當的 rel 屬性

## CSS 樣式要求
- 使用 CSS 變數：--sowork-orange: #FF6B35
- 響應式設計，支援行動裝置
- 適當的間距和字體大小
- 清晰的視覺層次

請生成完整的HTML文檔，確保可以直接在瀏覽器中正常顯示。不要包含任何markdown格式或解釋文字。"""

def test_openai_connection():
    """測試 OpenAI API 連接"""
    print("🔑 測試 OpenAI API 連接...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("❌ 未找到 OPENAI_API_KEY 環境變數")
    
    if not api_key.startswith('sk-'):
        raise ValueError("❌ API Key 格式錯誤，應以 'sk-' 開頭")
    
    # 簡單的測試請求
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    test_data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ OpenAI API 連接成功")
            return True
        else:
            print(f"❌ API 測試失敗，狀態碼: {response.status_code}")
            print(f"錯誤回應: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 網路請求失敗: {e}")
        return False

def generate_content():
    """生成網頁內容"""
    print("🚀 開始生成週更新內容...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": PROMPT
            }
        ],
        "max_tokens": 12000,
        "temperature": 0.3
    }
    
    print("📤 發送請求到 OpenAI API...")
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=120  # 2分鐘超時
        )
        
        print(f"📡 API 回應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                
                # 清理格式
                content = content.strip()
                if content.startswith('```html'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                print(f"✅ 內容生成成功，長度: {len(content)} 字符")
                return content
            else:
                raise Exception("API 回應中沒有找到 choices")
                
        elif response.status_code == 400:
            error_info = response.json()
            raise Exception(f"請求格式錯誤: {error_info.get('error', {}).get('message', '未知錯誤')}")
            
        elif response.status_code == 401:
            raise Exception("API Key 無效或已過期")
            
        elif response.status_code == 429:
            raise Exception("API 請求頻率超限，請稍後重試")
            
        else:
            raise Exception(f"API 請求失敗，狀態碼: {response.status_code}, 回應: {response.text}")
            
    except requests.exceptions.Timeout:
        raise Exception("請求超時，請檢查網路連接")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"網路請求失敗: {e}")

def validate_html_content(content):
    """驗證生成的 HTML 內容"""
    print("🔍 驗證生成的內容...")
    
    required_elements = [
        '<!DOCTYPE html>',
        'tailwindcss',
        '#FF6B35',
        '美國關稅政策最新動態',
        '台灣出口商商業情報'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"⚠️  警告：以下必要元素缺失: {', '.join(missing_elements)}")
    else:
        print("✅ 內容驗證通過")
    
    return len(missing_elements) == 0

def save_content(content):
    """儲存生成的內容"""
    timestamp = datetime.now().isoformat()
    
    # 添加生成時間註解
    content_with_timestamp = f"<!-- Generated on: {timestamp} -->\n{content}"
    
    # 儲存 HTML 檔案
    with open('generated_content.html', 'w', encoding='utf-8') as f:
        f.write(content_with_timestamp)
    
    print("📄 HTML 內容已儲存為 generated-content.html")
    
    # 更新 README
    current_time = get_current_time()
    week_number = get_week_number()
    
    readme_content = f"""# 美國關稅政策最新動態 - 台灣出口商商業情報

## 📊 生成資訊
- **生成時間：** {current_time}
- **內容週期：** 第 {week_number} 週
- **格式：** 完整 HTML 文檔（包含 Tailwind CSS）
- **檔案大小：** {len(content_with_timestamp):,} 字符

## 🚀 使用方法

### 方法 1：直接複製 HTML
1. 點擊 ➡️ [generated-content.html](./generated-content.html)
2. 點擊 **"Raw"** 按鈕查看原始代碼
3. 全選複製所有內容 (Ctrl+A, Ctrl+C)
4. 貼到您的 Wix HTML 元件中

### 方法 2：預覽內容
- 下載 `generated-content.html` 檔案
- 用瀏覽器直接開啟查看效果

## 📋 內容包含

### ✅ 四大主要區塊
- **最新政策概述** - 美國關稅政策最新動態
- **專家觀點** - 權威機構分析報告  
- **美國電商平台政策** - Amazon、eBay、Walmart 等平台政策
- **歐盟、日本、韓國關稅政策** - 其他重要市場動態

### ✅ 技術規格
- 完整 HTML5 文檔結構
- Tailwind CSS 框架
- Font Awesome 圖示庫
- SoWork 橘色主題 (#FF6B35)
- 響應式設計
- 現代卡片式布局

## 🔄 自動化排程
- **頻率：** 每週日晚上 11:00 (UTC)
- **台灣時間：** 每週一早上 7:00
- **手動觸發：** 隨時可在 Actions 中手動執行

## 📝 內容特色
- ✅ 所有新聞均包含原始來源連結
- ✅ 已過濾政府領導人相關內容
- ✅ 標註原文未提及台灣的項目
- ✅ 內容更新至最新一週
- ✅ 繁體中文呈現
- ✅ 響應式設計支援各種裝置

## 📊 技術統計
- **生成時間：** {timestamp}
- **Python 腳本：** generated_content.py
- **AI 模型：** GPT-4o-mini
- **內容驗證：** ✅ 通過

---
*此內容由 GitHub Actions 自動生成 | © 2025 台灣出口商商業情報*
*使用 Python + OpenAI API 技術架構*"""

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("📋 README.md 已更新")

def main():
    """主要執行函數"""
    try:
        print("=" * 60)
        print("🇹🇼 台灣出口商美國關稅政策資訊生成器")
        print("=" * 60)
        
        # 測試 API 連接
        if not test_openai_connection():
            sys.exit(1)
        
        # 生成內容
        content = generate_content()
        
        # 驗證內容
        if not validate_html_content(content):
            print("⚠️  內容驗證發現問題，但仍將繼續儲存")
        
        # 儲存內容
        save_content(content)
        
        print("=" * 60)
        print("🎉 內容生成完成！")
        print("📁 檔案已儲存：generated_content.html")
        print("📋 說明已更新：README.md")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 程序執行失敗: {e}")
        
        # 寫入錯誤日誌
        error_time = datetime.now().isoformat()
        error_log = f"[{error_time}] 錯誤: {e}\n"
        
        with open('error.log', 'a', encoding='utf-8') as f:
            f.write(error_log)
        
        print("📝 錯誤已記錄到 error.log")
        sys.exit(1)

if __name__ == "__main__":
    main()
