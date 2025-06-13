const fs = require('fs');
const https = require('https');

// 您的提示詞
const PROMPT = `## 網頁更新指令

請使用與參考示例完全相同的設計方式，創建一個台灣出口商的美國關稅政策資訊網頁，並將所有數據更新至最新。

1. 視覺設計規範
- 使用GQ Business的現代簡潔風格
- 主色調為SoWork數據市調的橘色(#FF6B35) 
- 必須使用完整的HTML文檔結構，包含<!DOCTYPE html>
- 必須引入Tailwind CSS: <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
- 必須引入Font Awesome: <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
- 保持四個區塊的布局結構不變
- 維持原有的字體、間距和視覺層次
- 保持清晰的模塊化區域劃分和卡片式設計

2. 技術規範
- 使用完整的HTML5文檔結構
- CSS變數設定：--sowork-orange: #FF6B35
- 新聞卡片必須有hover效果：transform: translateY(-3px)
- 日期徽章使用橘色背景，來源徽章使用灰色背景
- 響應式設計支援行動裝置
- 包含適當的meta標籤和viewport設定

3. 內容規範
- **最新政策概述**：包含從上週至今的新聞，按時間排序，以繁體中文呈現
- **專家觀點**：只包含上週至今來自權威機構的分析，若原文未提及台灣則摘要中也不提及
- **美國電商平台的政策**：只包含上週至今的相關資訊
- **歐盟、日本、韓國的關稅政策**：只包含上週至今的消息

4. 內容準則
- 所有摘要必須忠實反映原始報導內容，不添加推測或解釋
- 每篇新聞都需標明日期、來源和原始連結
- 不包含任何政府領導人相關內容
- 如果原文未直接提及台灣，需要標註說明

5. 結構要求
- Header: 包含主標題、副標題、更新日期
- Main: 四個section，使用白色卡片背景和陰影效果
- 每個新聞項目包含：日期徽章、來源徽章、標題、內容、連結
- Footer: 版權資訊和更新時間
- 使用Font Awesome圖示增強視覺效果

6. 輸出要求
- 標題: 美國關稅政策最新動態 - 台灣出口商商業情報
- 生成完整的HTML文檔，可直接在瀏覽器中開啟
- 不要包含任何markdown格式或解釋文字
- 確保所有CSS樣式內嵌在<style>標籤中

請嚴格按照以上規範生成完整的HTML文檔，確保格式完全符合現代網頁標準。`;

async function generateContent() {
    console.log('🚀 開始生成週更新內容...');
    
    const data = JSON.stringify({
        model: "gpt-4o-mini",  // 改回較穩定的模型
        messages: [
            {
                role: "user",
                content: PROMPT
            }
        ],
        max_tokens: 12000,  // 稍微降低 token 數量
        temperature: 0.3
    });

    const options = {
        hostname: 'api.openai.com',
        port: 443,
        path: '/v1/chat/completions',
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
            'Content-Type': 'application/json',
            'Content-Length': data.length
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let responseData = '';

            console.log(`📡 API 回應狀態: ${res.statusCode}`);

            res.on('data', (chunk) => {
                responseData += chunk;
            });

            res.on('end', () => {
                try {
                    // 輸出原始回應以便診斷
                    console.log('📄 API 回應長度:', responseData.length);
                    
                    // 檢查是否是 JSON
                    if (!responseData.trim().startsWith('{')) {
                        console.error('❌ 非 JSON 回應:', responseData.substring(0, 500));
                        reject(new Error('API 回應不是 JSON 格式'));
                        return;
                    }

                    const response = JSON.parse(responseData);
                    
                    // 檢查錯誤
                    if (response.error) {
                        console.error('❌ OpenAI API 錯誤:', response.error);
                        reject(new Error(`OpenAI API 錯誤: ${response.error.message}`));
                        return;
                    }
                    
                    // 檢查回應結構
                    if (!response.choices || !response.choices[0] || !response.choices[0].message) {
                        console.error('❌ 無效的回應結構:', JSON.stringify(response, null, 2));
                        reject(new Error('API 回應缺少必要欄位'));
                        return;
                    }
                    
                    let content = response.choices[0].message.content;
                    
                    if (!content) {
                        reject(new Error('API 回應內容為空'));
                        return;
                    }
                    
                    console.log('✅ 內容生成成功，長度:', content.length);
                    
                    // 清理格式
                    content = content.replace(/```html\n?/g, '');
                    content = content.replace(/```\n?$/g, '');
                    content = content.trim();
                    
                    resolve(content);
                    
                } catch (error) {
                    console.error('❌ JSON 解析錯誤:', error.message);
                    console.error('📄 原始回應開頭:', responseData.substring(0, 1000));
                    reject(new Error(`JSON 解析失敗: ${error.message}`));
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ 請求錯誤:', error.message);
            reject(new Error(`請求失敗: ${error.message}`));
        });

        req.write(data);
        req.end();
    });
}

async function main() {
    try {
        const htmlContent = await generateContent();
        
        // 添加生成時間戳記
        const timestamp = new Date().toISOString();
        const contentWithTimestamp = `<!-- Generated on: ${timestamp} -->\n${htmlContent}`;
        
        // 儲存到檔案
        fs.writeFileSync('generated-content.html', contentWithTimestamp, 'utf8');
        
        // 創建簡易的檢視檔案
        const readmeContent = `# 最新生成的內容

生成時間：${new Date().toLocaleString('zh-TW')}

## 使用方法：
1. 複製 \`generated-content.html\` 中的內容
2. 貼到您的 Wix 網站中
3. 發布更新

## 檔案：
- [generated-content.html](./generated-content.html) - 生成的 HTML 內容

---
*此內容由 GitHub Actions 自動生成*`;

        fs.writeFileSync('README.md', readmeContent, 'utf8');
        
        console.log('✅ 內容生成完成！');
        console.log('📄 檔案已儲存為 generated-content.html');
        
    } catch (error) {
        console.error('❌ 生成失敗:', error);
        process.exit(1);
    }
}

main();
