"""
图片生成工具
支持图生图功能，将用户照片与商品照片合成为营销图片
支持一次性生成4张同一场景下不同角度的图片
"""
import random
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import ImageGenerationClient
from coze_coding_utils.runtime_ctx.context import new_context


# 真实感增强关键词库（强化版）
REALISM_ENHANCERS = [
    # 质感相关
    "像真实拍摄", "真实质感", "自然肤色", "轻度后期", "保留纹理",
    "生活化", "自然过渡", "真实细节", "生活气息", "像摄影师拍摄",
    # 人物互动相关
    "人物正在使用商品", "手部自然接触", "眼神自然交流", "表情与使用场景协调",
    "自然握持", "真实互动", "使用状态", "展示状态",
]

# 场景关键词库（统一场景）
SCENE_STYLES = [
    "温馨咖啡馆午后场景", "办公室工位一角", "客厅沙发休息区", 
    "阳台阳光区", "卧室床头", "餐厅餐桌旁",
]

# 4张图片的拍摄角度（固定分配）
FOUR_SHOT_ANGLES = [
    {
        "name": "45度侧拍中景",
        "description": "45度侧拍中景构图，展示整体场景和人物商品关系",
        "focus": "整体互动"
    },
    {
        "name": "特写镜头",
        "description": "特写镜头聚焦商品，突出商品细节，人物手部自然接触商品",
        "focus": "商品细节"
    },
    {
        "name": "俯拍视角",
        "description": "俯拍视角展现人物与商品的互动，不同视角的展示效果",
        "focus": "互动视角"
    },
    {
        "name": "第一视角",
        "description": "第一视角手持商品，强代入感，仿佛用户自己使用",
        "focus": "代入体验"
    },
]

# 光线质感关键词库（统一光线）
LIGHTING_STYLES = [
    "自然窗边散射光，统一光线方案",
    "柔和室内环境光，真实阴影",
    "温暖午后自然光，真实反光",
    "适度环境光，自然色温",
]

# 人物互动关键词库
INTERACTION_STYLES = [
    "人物正在使用商品，手部自然握持",
    "人物手持商品展示，眼神看向商品",
    "人物手指轻触商品，动作自然",
    "人物专注于商品，表情自然放松",
]


def enhance_prompt_for_realism(prompt: str, index: int, scene: str) -> str:
    """
    为4张图片分别增强提示词，确保同一场景、不同角度、真实互动
    
    Args:
        prompt: 原始提示词
        index: 图片索引（0-3）
        scene: 统一场景描述
    
    Returns:
        增强后的提示词
    """
    # 选择该图片的拍摄角度配置
    angle_config = FOUR_SHOT_ANGLES[index]
    
    # 选择光线风格
    lighting = LIGHTING_STYLES[index % len(LIGHTING_STYLES)]
    
    # 选择互动风格
    interaction = INTERACTION_STYLES[index % len(INTERACTION_STYLES)]
    
    # 选择真实感增强（2个）
    selected_realism = random.sample(REALISM_ENHANCERS, 2)
    
    # 构建完整描述
    enhanced_prompt = (
        f"{scene}，{angle_config['description']}，{lighting}，"
        f"{interaction}，{' '.join(selected_realism)}，"
        f"保留真实细节，不过度美化，像真实拍摄的营销照片"
    )
    
    # 添加用户原始提示词（如果有的话）
    if prompt and prompt.strip():
        enhanced_prompt += f"，{prompt.strip()}"
    
    # 确保提示词不超过长度限制
    if len(enhanced_prompt) > 500:
        enhanced_prompt = enhanced_prompt[:500]
    
    return enhanced_prompt


@tool
def generate_marketing_image_batch(prompt: str, user_photo_url: str, product_photo_url: str, runtime: ToolRuntime=None) -> str:
    """
    一次性生成4张同一场景下不同角度的社交媒体营销图片
    
    Args:
        prompt: 图片生成提示词，描述想要的风格和效果
        user_photo_url: 用户照片的URL
        product_photo_url: 商品照片的URL
        runtime: 工具运行时上下文
    
    Returns:
        生成的4张图片URL，用换行符分隔
    """
    ctx = new_context(method="generate_marketing_image_batch")
    
    client = ImageGenerationClient(ctx=ctx)
    
    # 随机选择一个统一场景
    scene = random.choice(SCENE_STYLES)
    
    # 为4张图片分别生成提示词
    image_urls = []
    
    for i in range(4):
        # 增强提示词
        enhanced_prompt = enhance_prompt_for_realism(prompt, i, scene)
        
        try:
            # 生成单张图片
            response = client.generate(
                prompt=enhanced_prompt,
                image=[user_photo_url, product_photo_url],
                size="2K",
                watermark=False,
                response_format="url"
            )
            
            if response.success and response.image_urls:
                image_urls.append(response.image_urls[0])
            else:
                error_msg = ", ".join(response.error_messages) if response.error_messages else "Unknown error"
                image_urls.append(f"第{i+1}张图片生成失败: {error_msg}")
        except Exception as e:
            image_urls.append(f"第{i+1}张图片生成异常: {str(e)}")
    
    # 返回4张图片的URL（用换行符分隔）
    return "\n".join(image_urls)


# 保留原函数名以保持兼容性
@tool
def generate_marketing_image(prompt: str, user_photo_url: str, product_photo_url: str, runtime: ToolRuntime=None) -> str:
    """
    生成社交媒体营销图片（兼容版本，调用批量生成）
    
    Args:
        prompt: 图片生成提示词，描述想要的风格和效果
        user_photo_url: 用户照片的URL
        product_photo_url: 商品照片的URL
        runtime: 工具运行时上下文
    
    Returns:
        生成的4张图片URL，用换行符分隔
    """
    # 调用批量生成函数
    return generate_marketing_image_batch(prompt, user_photo_url, product_photo_url, runtime)
