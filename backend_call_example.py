import requests
import json
import sseclient  # 需要安装 sseclient-py: pip install sseclient-py
from openai import OpenAI
import os

BASE_URL = "http://localhost:8888"

# 重要提示：
# 在运行服务之前，必须设置环境变量 COZE_WORKLOAD_IDENTITY_API_KEY 为有效的 Coze API Key。
# 否则可能会遇到 401 或 500 错误。
# 示例: export COZE_WORKLOAD_IDENTITY_API_KEY=pat_xxxxxx

def call_sync_run():
    """
    示例 1: 同步调用 /run 接口
    适用于不需要流式输出的场景，等待整个任务完成后返回结果。
    """
    print("\n--- 示例 1: 同步调用 /run ---")
    url = f"{BASE_URL}/run"
    
    # 构造 LangGraph 的输入格式
    payload = {
        "messages": [
            {"role": "user", "content": "你好，请介绍一下你自己"}
        ],
        "configurable": {
            "thread_id": "user-123" # 用于记忆功能的会话ID
        }
    }
    
    try:
        print(f"POST {url}")
        response = requests.post(url, json=payload)
        
        if response.status_code == 500:
            print(f"Server Error 500: 可能缺少有效的 COZE_WORKLOAD_IDENTITY_API_KEY 环境变量")
            print(response.text)
            return

        response.raise_for_status()
        result = response.json()
        
        # 打印最后一条消息的内容
        if "messages" in result:
            last_message = result["messages"][-1]
            print(f"Agent 回复: {last_message['content']}")
        else:
            print(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
    except Exception as e:
        print(f"调用失败: {e}")

def call_stream_run():
    """
    示例 2: 流式调用 /stream_run 接口 (SSE)
    适用于需要实时显示打字机效果的场景。
    """
    print("\n--- 示例 2: 流式调用 /stream_run ---")
    url = f"{BASE_URL}/stream_run"
    
    payload = {
        "messages": [
            {"role": "user", "content": "讲一个关于程序员的笑话"}
        ],
        "configurable": {
            "thread_id": "user-123"
        }
    }
    
    try:
        print(f"POST {url} (stream=True)")
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
        
        client = sseclient.SSEClient(response)
        print("Agent 回复: ", end="", flush=True)
        
        for event in client.events():
            if event.data:
                try:
                    data = json.loads(event.data)
                    # 根据具体的 SSE 数据结构解析
                    # 这里假设数据结构可能包含 content 或 delta
                    # 实际结构取决于 LangGraph 的 stream 输出
                    if isinstance(data, dict):
                        # 处理消息更新
                        if "messages" in data:
                             # 这里简化处理，实际可能需要更复杂的解析
                             pass
                        elif "content" in data:
                             print(data["content"], end="", flush=True)
                    else:
                        print(data, end="", flush=True)
                except json.JSONDecodeError:
                    pass
        print() # 换行
            
    except Exception as e:
        print(f"调用失败: {e}")

def call_openai_compatible():
    """
    示例 3: 使用 OpenAI SDK 调用 /v1/chat/completions 接口
    适用于已经集成了 OpenAI SDK 的项目，只需修改 base_url 和 api_key。
    注意：Agent 可能需要 session_id，可以通过 extra_body 传入。
    """
    print("\n--- 示例 3: OpenAI SDK 兼容调用 ---")
    
    client = OpenAI(
        base_url=f"{BASE_URL}/v1",
        api_key="sk-xxxx", # 任意非空字符串
    )
    
    try:
        print(f"Calling OpenAI API...")
        response = client.chat.completions.create(
            model="default", # 模型名称任意
            messages=[
                {"role": "user", "content": "用 Python 写一个 Hello World"}
            ],
            stream=True, # 支持流式
            extra_body={
                "configurable": {
                    "session_id": "user-123" # 必需参数
                }
            }
        )
        
        print("Agent 回复: ", end="", flush=True)
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()
        
    except Exception as e:
        print(f"调用失败: {e}")

if __name__ == "__main__":
    # 请确保服务已在 8888 端口启动
    # export COZE_WORKSPACE_PATH=$(pwd) && export COZE_WORKLOAD_IDENTITY_API_KEY=your_key && ./scripts/http_run.sh -p 8888
    
    call_sync_run()
    # call_stream_run() # 需要安装 sseclient-py
    call_openai_compatible()
