undefinedconst fs = require('fs');
const https = require('https');

// 您的提示詞
const PROMPT = `網頁更新指令

請創建一個台灣出口商的美國關稅政策資訊網頁，將所有數據更新至最新。

1. 視覺設計規範
- 使用現代簡潔風格
- 主色調為橘色(#FF7A00)
- 採用四個區塊的布局結構：最新政策概述、專家觀點、美國電商平台政策、歐盟日本韓國關稅政策
- 每個區塊包含標題、內容摘要、時間戳記、來源連結

2. 內容規範
- 最新政策概述：包含從上週至今的新聞，按時間排序，以繁體中文呈現
- 專家觀點：只包含上週至今來自權威機構的分析
- 美國電商平台的政策：只包含上週至今的相關資訊
- 歐盟、日本、韓國的關稅政策：只包含上週至今的消息

3. 內容準則
- 所有摘要必須忠實反映原始報導內容
- 每篇新聞都需標明日期、來源和原始連結
- 不包含任何政府資源連結

4. 輸出要求
- 標題: 美國關稅政策最新動態 - 台灣出口商商業情報
- 請只回傳完整的HTML代碼，包含完整的CSS樣式
- 使用響應式設計，支援各種螢幕尺寸
- 不要包含任何解釋文字，不要使用markdown格式`;

async function generateContent() {
    console.log('🚀 開始生成週更新內容...');
    
    const data = JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
            {
                role: "user",
                content: PROMPT
            }
        ],
        max_tokens: 8000,
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

            res.on('data', (chunk) => {
                responseData += chunk;
            });

            res.on('end', () => {
                try {
                    const response = JSON.parse(responseData);
                    if (response.choices && response.choices[0]) {
                        let content = response.choices[0].message.content;
                        
                        // 清理格式
                        content = content.replace(/```html\n?/g, '').replace(/```\n?$/g, '').trim();
                        
                        resolve(content);
                    } else {
                        reject(new Error('Invalid API response'));
                    }
                } catch (error) {
                    reject(error);
                }
            });
        });

        req.on('error', (error) => {
            reject(error);
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
