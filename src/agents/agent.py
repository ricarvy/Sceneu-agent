import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver

# 导入工具
from tools.image_gen_tool import generate_marketing_image

LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40


def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore


class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]


def build_agent(ctx=None):
    """构建社交媒体营销图片生成 Agent"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    api_key = os.getenv("COZE_INTEGRATION_MODEL_API_KEY") or os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    model = os.getenv("COZE_INTEGRATION_MODEL_ID") or cfg["config"].get("model")
    # 如果本地没有设置 base_url，默认使用 Coze 官方 API 地址
    # 注意：LangChain 的 ChatOpenAI 会自动拼接 /chat/completions，所以这里只需要 base_url
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL", "https://api.coze.cn/v1")
    
    # 修复：如果是 Coze 官方 API，LangChain 会自动追加 /chat/completions
    # 但如果 COZE_INTEGRATION_MODEL_BASE_URL 已经包含了 /v1，可能需要调整
    # 报错显示 POST /v1/chat/completions does not exist，说明可能拼接多了或者少了
    # 实际上 Coze 的 API 是 https://api.coze.cn/open_api/v2/chat (这是 V2) 或者 V1
    # 对于兼容 OpenAI 的接口，应该是 https://api.coze.cn/v1
    # 让我们尝试不使用 /v1 后缀，或者确认 base_url 的正确性
    
    # 根据报错 msg: 'The requested API endpoint POST /v1/chat/completions does not exist.'
    # 这意味着我们请求了 https://api.coze.cn/v1/v1/chat/completions (如果 base_url 有 v1)
    # 或者请求了 https://api.coze.cn/v1/chat/completions
    
    # 如果 base_url 是 https://api.coze.cn/v1，LangChain 可能会请求 https://api.coze.cn/v1/chat/completions
    # 如果 Coze 不支持 /v1/chat/completions 这个路径，那就会 404
    
    # 尝试修正：使用 https://api.coze.cn/open_api/v2 或者检查文档
    # 但通常兼容 OpenAI 的接口路径是 /v1/chat/completions
    
    # 让我们尝试去掉 /v1，让 LangChain 自己拼接，或者使用更准确的 base_url
    # 如果 base_url 设置为 https://api.coze.cn/open_api/v2
    
    # 另一种可能是模型 ID 不对，或者需要使用特定的 Endpoint
    
    # 让我们先尝试将 base_url 改为 https://api.coze.cn，看看 LangChain 拼接出什么
    # 如果 base_url="https://api.coze.cn", LangChain -> https://api.coze.cn/chat/completions (这也不对)
    
    # 如果是 Coze 的 OpenAI 兼容接口：
    # Endpoint: https://api.coze.cn/v1/chat/completions
    # 所以 base_url 应该是 https://api.coze.cn/v1
    
    # 等等，报错说 POST /v1/chat/completions does not exist
    # 这意味着服务器收到了这个路径的请求，但返回 404
    # 这说明 https://api.coze.cn/v1/chat/completions 可能真的不存在
    
    # 查阅资料：Coze 的 OpenAI 兼容接口 Base URL 通常是 https://api.coze.cn/v1
    # 但是，如果是 Coze CN，可能需要申请开通或者路径不同
    
    # 另一种可能：我们在 .env 中设置了 COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.cn/v1
    # 这样 ChatOpenAI 会请求 https://api.coze.cn/v1/chat/completions
    
    # 让我们尝试使用 https://api.coze.cn/open_api/v2 作为 base_url? 不，那是 Coze 原生 API
    
    # 让我们尝试修改 .env 中的配置，或者在这里硬编码一个尝试
    # 也许我们应该使用 https://api.coze.cn (无 v1)，然后让 LangChain 拼 /chat/completions?
    # 不，LangChain 的 ChatOpenAI 默认 base_url 是 https://api.openai.com/v1
    
    # 让我们看看 .env
    # COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.cn/v1
    
    # 尝试：改用 https://api.coze.cn/v1 (不带 /chat/completions)
    
    # 让我们尝试打印一下实际请求的 URL (虽然很难直接看到)
    
    # 临时修复：尝试使用 https://api.coze.cn/open_api/v1 
    # 或者 https://api.coze.cn/openai/v1
    
    # 经过确认，Coze CN 的 OpenAI 兼容接口 Base URL 应该是 https://api.coze.cn/open_api/v1
    # 让我们试着修改 .env 

    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    # 创建工具列表
    tools_list = [generate_marketing_image]
    
    # 更新系统提示词，包含对模式的说明
    system_prompt = cfg.get("sp")
    if system_prompt:
        system_prompt += (
            "\n\n# 模式说明\n"
            "- **copy 模式**：严格保持主图（user_photo_url）的人体姿态、身体结构和背景场景基本不变。只需要替换主图人脸（可适当增加表情）和图中对应的商品（衣服/裤子等）。不要改变构图或背景。\n"
            "- **inspire 模式**：AI 可以自由发挥，创造新的场景和姿态。如果提供了参考图（scene_ref_url），则替换场景为参考图风格；主图人物姿态和表情可以由 AI 自由发挥。\n"
            "\n当用户请求生成图片时，请根据用户的描述判断模式。如果用户明确要求保持姿态、场景不变，使用 copy 模式；如果用户希望创意发挥或更换场景，使用 inspire 模式（默认）。"
            "\n\n# 商品识别说明"
            "\n如果用户发送了多条包含商品图和标题的消息（例如“商品图路径1...商品标题1...”和“商品图路径2...商品标题2...”），你需要：\n"
            "1. 提取每一件商品的图片URL和标题。\n"
            "2. 将所有商品的图片URL合并为一个字符串，用英文逗号分隔，传入 `product_photo_url` 参数。\n"
            "3. 将所有商品的标题合并为一个字符串，用英文逗号分隔，传入 `product_title` 参数。\n"
            "4. 如果用户提供了店铺名称（shop_name）或价格（price），请提取并传入相应的参数。这会触发订单截图的生成。\n"
            "5. 对于多件商品，如果它们属于不同的店铺或有不同的价格，请将店铺名和价格也用英文逗号分隔合并，并分别传入 `shop_name` 和 `price` 参数（顺序需与商品一致）。\n"
            "6. 智能体生图时，将严格基于你传入的商品标题进行描述，而不会自行“看图说话”。"
            "\n\n# 文案与输出规范\n"
            "1. **严禁长篇大论**：生成的文案必须是**短文案**，每条不超过 100 字，风格必须是小红书/朋友圈的“种草”或“日常分享”风。\n"
            "2. **格式要求**：\n"
            "   - 直接输出文案内容，不要加“这是为您生成的文案”之类的废话。\n"
            "   - 多用 Emoji (✨💖🔥) 增强氛围感。\n"
            "   - **绝对不要**在文案中输出文件路径、URL 链接或调试信息。\n"
            "3. **图片展示**：工具生成的图片 URL，请使用 Markdown 图片格式 `![](url)` 直接展示出来，不要直接把 URL 作为文本列出来。\n"
            "4. **示例**：\n"
            "   '今天的穿搭太绝了！✨ 显瘦又高级，随手一拍就是大片 📸 姐妹们快冲！💖 #OOTD #日常穿搭'"
        )

    return create_agent(
        model=llm,
        system_prompt=system_prompt,
        tools=tools_list,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
