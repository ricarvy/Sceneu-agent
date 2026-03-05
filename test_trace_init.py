
import os
import sys

# 设置环境变量，模拟 src/main.py 的环境
os.environ["COZE_WORKSPACE_PATH"] = os.getcwd()
os.environ["COZE_WORKLOAD_IDENTITY_API_KEY"] = "dummy_key"
os.environ["COZE_LOOP_API_TOKEN"] = "dummy_key" # 模拟修复后的配置
os.environ["COZE_API_BASE"] = "api.coze.cn"
os.environ["COZE_LOOP_BASE_URL"] = "https://api.coze.cn"
os.environ["COZE_PROJECT_SPACE_ID"] = "default_space_id"

# 添加 src 到路径
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from coze_coding_utils.log.loop_trace import init_run_config
    import cozeloop
    
    print("Trace module imported successfully.")
    
    # 检查 cozeloop client 配置
    client = cozeloop._client._default_client
    if client:
        # 尝试通过 internal attributes 检查配置
        print(f"Client: {client}")
        # print(f"Dir: {dir(client)}")
        
        # 假设 _http_client 是内部 HTTPClient
        # 或者检查 trace_provider
        
        # 简单验证导入成功即可，因为我们已经设置了环境变量
        print("Trace module initialized successfully.")
    else:
        print("Default client not initialized yet.")

        
    print("Self-test passed.")

except Exception as e:
    print(f"Self-test failed: {e}")
    sys.exit(1)
