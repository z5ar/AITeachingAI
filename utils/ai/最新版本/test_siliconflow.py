import requests
import json

def test_siliconflow_api():
    """测试SiliconFlow API连接"""
    api_key = "达咩"  # 请替换为实际的API密钥
    url = "https://api.siliconflow.cn/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-ai/DeepSeek-V3",  # 使用DeepSeek-V3模型[citation:4]
        "messages": [
            {
                "role": "user", 
                "content": "请用一句话介绍你自己"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        print("测试SiliconFlow API连接...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API测试成功!")
            print(f"AI回复: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ API测试失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    test_siliconflow_api()