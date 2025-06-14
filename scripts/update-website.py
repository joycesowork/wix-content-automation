import os
import openai
from datetime import datetime
import re

def load_prompt():
    """載入更新指令"""
    with open('prompts/關稅新聞.txt', 'r', encoding='utf-8') as f:
        return f.read()

def load_template():
    """載入原始HTML模板"""
    with open('templates/關稅新聞.html', 'r', encoding='utf-8') as f:
        return f.read()

def call_openai_api(prompt, template):
    """呼叫 OpenAI API"""
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    full_prompt = f"""
{prompt}

以下是需要更新的原始HTML模板：

{template}

請嚴格按照上述指令更新內容，直接輸出完整的HTML代碼：
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # 或 "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "你是一個專業的網站內容更新助手。"},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=8000,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"API 呼叫失敗: {e}")
        return None

def save_updated_html(content):
    """儲存更新後的HTML"""
    # 確保 docs 目錄存在
    os.makedirs('docs', exist_ok=True)
    
    # 生成檔案名稱
    current_date = datetime.now()
    filename = f"taiwan_export_tariff_news_{current_date.strftime('%Y%m')}.html"
    filepath = os.path.join('docs', filename)
    
    # 儲存檔案
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 同時儲存為 index.html (用於 GitHub Pages)
    index_path = os.path.join('docs', 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"HTML 已儲存至: {filepath}")
    print(f"GitHub Pages 版本已儲存至: {index_path}")

def validate_html(content):
    """驗證HTML格式是否正確"""
    if not content:
        return False
    
    # 基本HTML結構檢查
    required_elements = [
        '<html',
        '<head>',
        '<body>',
        'sowork-orange',
        'news-card',
        '美國關稅政策最新動態'
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"警告: 缺少必要元素 {element}")
            return False
    
    return True

def main():
    print("開始更新網站內容...")
    
    # 載入prompt和模板
    prompt = load_prompt()
    template = load_template()
    
    # 呼叫API更新內容
    updated_content = call_openai_api(prompt, template)
    
    if updated_content and validate_html(updated_content):
        # 儲存更新後的HTML
        save_updated_html(updated_content)
        print("網站內容更新完成！")
    else:
        print("更新失敗：生成的內容不符合要求")
        exit(1)

if __name__ == "__main__":
    main()
