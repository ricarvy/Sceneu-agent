
import os
import json
from dotenv import load_dotenv
from coze_coding_dev_sdk import ImageGenerationClient

load_dotenv()

def test_image_gen():
    print("Testing Image Generation Client...")
    
    # 打印关键环境变量 (脱敏)
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_BASE_URL")
    print(f"COZE_WORKLOAD_IDENTITY_API_KEY: {api_key[:10]}..." if api_key else "None")
    print(f"COZE_INTEGRATION_BASE_URL: {base_url}")
    
    client = ImageGenerationClient()
    
    try:
        # 尝试最简单的生成
        # 注意：这里需要确认 ImageGenerationClient.generate 的正确签名
        # 如果是 Coze SDK，通常它会封装具体 API 调用
        # 假设这里是调用 Coze 的图像生成能力
        
        # 构造一个简单的请求
        # 如果没有真实图片 URL，可能需要用网上的公开图片或者 mock
        # 这里用一个简单的 prompt 测试文生图能力 (如果支持)
        
        resp = client.generate(
            prompt="A cute cat",
            # 可能需要其他参数，视 SDK 而定
        )
        print("Response:", resp)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_gen()
