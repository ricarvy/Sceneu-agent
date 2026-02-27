"""
图片生成工具
支持图生图功能，将用户照片与商品照片合成为营销图片
支持一次性生成4张同一场景下不同角度的图片
突出用户使用商品的体验和多样性
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
    "自然握持", "真实互动", "使用状态", "展示状态", "享受体验",
]

# 场景关键词库（多样化场景）
SCENE_STYLES = [
    "温馨咖啡馆午后场景", "办公室工位一角", "客厅沙发休息区", 
    "阳台阳光区", "卧室床头", "餐厅餐桌旁",
    "户外公园长椅", "书店阅读区", "地铁站通勤中",
]

# 4张图片的使用场景和角度配置（多样性优先）
FOUR_SHOT_SCENES = [
    {
        "name": "整体使用场景",
        "shot_type": "中景/全身",
        "distance": "中距离",
        "angle": "45度侧拍",
        "description": "中景全身构图，展示人物完整使用商品的场景，展现整体体验感",
        "focus": "整体使用体验"
    },
    {
        "name": "细节互动",
        "shot_type": "近景/半身",
        "distance": "近距离",
        "angle": "特写",
        "description": "近景半身构图，聚焦人物与商品的互动细节，突出商品质感和手部动作",
        "focus": "互动细节"
    },
    {
        "name": "远景氛围",
        "shot_type": "远景/全身",
        "distance": "远距离",
        "angle": "远景",
        "description": "远景全身构图，展现人物在环境中使用商品的整体氛围，适合有文字/logo的商品",
        "focus": "氛围场景"
    },
    {
        "name": "第一视角",
        "shot_type": "中近景",
        "distance": "中近距离",
        "angle": "第一视角",
        "description": "第一视角手持商品，强代入感，展现真实使用体验",
        "focus": "体验代入"
    },
]

# 表情多样性库（突出用户体验）
EXPRESSIONS = [
    "微笑满足的表情，享受使用商品",
    "专注认真的表情，沉浸在体验中",
    "惊喜愉悦的表情，发现商品的美好",
    "放松自然的表情，舒适的体验感",
    "自信优雅的表情，展现使用场景",
    "开心愉悦的表情，满意的效果",
]

# 使用动作多样性库
ACTION_STYLES = [
    "正在使用商品，动作流畅自然",
    "手持商品展示，姿态优雅",
    "调整商品细节，动作专注",
    "享受商品功能，表情满足",
    "与商品互动，手势自然",
    "体验商品效果，状态放松",
]

# 光线质感关键词库（统一光线但多样效果）
LIGHTING_STYLES = [
    "自然窗边散射光，真实柔和",
    "室内环境光，温暖舒适",
    "午后阳光，氛围感强",
    "柔和灯光，专业质感",
]

# 文字/Logo处理策略
TEXT_HANDLING = {
    "use_distant_shot": "远景构图，避免文字/logo细节问题",
    "slightly_blur": "适度虚化，保持整体视觉效果",
    "focus_on_experience": "聚焦人物体验，文字作为背景元素",
}

# 场景多样性（不同使用环境）
USE_ENVIRONMENTS = [
    "在家中使用，舒适温馨",
    "在办公室使用，专业高效",
    "在咖啡馆使用，休闲惬意",
    "在户外使用，阳光活力",
    "在通勤路上使用，便捷实用",
    "在休息区使用，放松自在",
]


def enhance_prompt_for_realism(prompt: str, index: int, scene: str) -> str:
    """
    为4张图片分别增强提示词，确保多样性、真实体验、表情丰富
    
    Args:
        prompt: 原始提示词
        index: 图片索引（0-3）
        scene: 统一场景描述
    
    Returns:
        增强后的提示词
    """
    # 选择该图片的场景配置（多样性优先）
    scene_config = FOUR_SHOT_SCENES[index]
    
    # 选择光线风格
    lighting = LIGHTING_STYLES[index % len(LIGHTING_STYLES)]
    
    # 选择表情（多样性）
    expression = random.choice(EXPRESSIONS)
    
    # 选择动作（多样性）
    action = random.choice(ACTION_STYLES)
    
    # 选择使用环境（多样性）
    environment = random.choice(USE_ENVIRONMENTS)
    
    # 选择真实感增强（2-3个）
    selected_realism = random.sample(REALISM_ENHANCERS, random.randint(2, 3))
    
    # 构建完整描述 - 突出使用体验和多样性
    enhanced_prompt_parts = [
        f"{scene}，{environment}",
        f"{scene_config['description']}，{scene_config['shot_type']}，{scene_config['angle']}",
        f"{expression}，{action}",
        f"{lighting}，{' '.join(selected_realism)}",
    ]
    
    # 添加文字处理策略（如果涉及远景）
    if scene_config['distance'] == "远距离":
        text_handling = TEXT_HANDLING["use_distant_shot"]
        enhanced_prompt_parts.append(text_handling)
    
    # 合并提示词
    enhanced_prompt = "，".join(enhanced_prompt_parts)
    
    # 添加用户原始提示词（如果有的话）
    if prompt and prompt.strip():
        enhanced_prompt += f"，{prompt.strip()}"
    
    # 确保提示词不超过长度限制
    if len(enhanced_prompt) > 500:
        enhanced_prompt = enhanced_prompt[:500]
    
    return enhanced_prompt


@tool
def generate_marketing_image(prompt: str, user_photo_url: str, product_photo_url: str, runtime: ToolRuntime=None) -> str:
    """
    一次性生成4张多样化场景、不同角度的社交媒体营销图片
    突出用户使用商品的体验，表情丰富，场景多样
    
    Args:
        prompt: 图片生成提示词，描述想要的风格和效果
        user_photo_url: 用户照片的URL
        product_photo_url: 商品照片的URL
        runtime: 工具运行时上下文
    
    Returns:
        生成的4张图片URL，用换行符分隔
    """
    ctx = new_context(method="generate_marketing_image")
    
    client = ImageGenerationClient(ctx=ctx)
    
    # 随机选择一个基础场景
    scene = random.choice(SCENE_STYLES)
    
    # 为4张图片分别生成提示词（多样性优先）
    image_urls = []
    
    for i in range(4):
        # 增强提示词 - 每张图片都有不同的体验和表情
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
