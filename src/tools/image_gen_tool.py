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

# 4张图片的使用场景和角度配置（多样性优先 + 明确区分）
FOUR_SHOT_SCENES = [
    {
        "name": "整体使用场景",
        "shot_type": "中景全身",
        "distance": "中距离",
        "angle": "45度侧拍",
        "description": "中景全身构图，人物在环境中使用商品，展现完整的使用场景和整体体验感，背景清晰可见",
        "focus": "整体使用体验",
        "unique_marker": "full_body_usage"
    },
    {
        "name": "细节互动特写",
        "shot_type": "近景半身",
        "distance": "近距离",
        "angle": "正面特写",
        "description": "近景半身构图，聚焦人物上半身与商品的互动细节，商品占据画面重要位置，突出商品质感和手部精细动作",
        "focus": "互动细节",
        "unique_marker": "close_up_interaction"
    },
    {
        "name": "远景氛围",
        "shot_type": "远景全身",
        "distance": "远距离",
        "angle": "远景广角",
        "description": "远景全身广角构图，展现人物在环境中的整体状态，环境占据较大比例，营造氛围感，适合有文字/logo的商品",
        "focus": "氛围场景",
        "unique_marker": "wide_angle_atmosphere"
    },
    {
        "name": "第一视角体验",
        "shot_type": "第一视角",
        "distance": "超近距离",
        "angle": "第一视角手持",
        "description": "第一视角手持商品，商品占据画面主体，仿佛用户自己正在使用，强代入感和沉浸感，背景虚化明显",
        "focus": "体验代入",
        "unique_marker": "first_person_pov"
    },
]

# 表情多样性库（突出用户体验 + 明确区分）
EXPRESSIONS = [
    {
        "expression": "微笑满足",
        "description": "微笑着使用商品，眼神温柔，嘴角上扬，表情满足愉悦，享受使用过程",
        "unique_marker": "smiling_satisfied"
    },
    {
        "expression": "专注认真",
        "description": "专注地看着商品或使用商品，眼神集中，表情认真，沉浸在使用体验中",
        "unique_marker": "focused_serious"
    },
    {
        "expression": "惊喜愉悦",
        "description": "眼神发光，表情惊喜，嘴角带笑，发现商品功能或效果的愉悦感",
        "unique_marker": "surprised_delighted"
    },
    {
        "expression": "放松自然",
        "description": "表情放松自然，眼神柔和，享受商品带来的舒适体验，姿态舒展",
        "unique_marker": "relaxed_natural"
    },
]

# 使用动作多样性库（明确区分）
ACTION_STYLES = [
    {
        "action": "正在使用",
        "description": "人物正在使用商品的核心功能，动作流畅自然，展示商品的使用方式",
        "unique_marker": "using_action"
    },
    {
        "action": "手持展示",
        "description": "人物手持商品展示给镜头，手势优雅，商品在画面中清晰可见",
        "unique_marker": "holding_display"
    },
    {
        "action": "调整细节",
        "description": "人物调整商品的细节，手指精细动作，表情专注，展示商品的可调节性",
        "unique_marker": "adjusting_action"
    },
    {
        "action": "享受体验",
        "description": "人物享受商品带来的体验，姿态放松，表情满足，展现商品效果",
        "unique_marker": "enjoying_action"
    },
]

# 光线质感关键词库（真实光影 + 高级感 + 明确区分）
LIGHTING_STYLES = [
    {
        "light": "自然窗边侧光",
        "description": "自然窗边侧光，侧面照射，真实阴影，勾勒人物轮廓，层次感强",
        "unique_marker": "side_light"
    },
    {
        "light": "室内环境散射光",
        "description": "室内环境散射光，色温真实，光线分布均匀，柔和自然",
        "unique_marker": "ambient_light"
    },
    {
        "light": "午后黄金时刻光",
        "description": "午后黄金时刻光，逆光光晕，真实反光，氛围温暖，光线有层次感",
        "unique_marker": "golden_hour_light"
    },
    {
        "light": "柔和顶光",
        "description": "柔和顶光，专业布光，真实阴影渐变，高光不过曝，暗部有细节",
        "unique_marker": "soft_top_light"
    },
]

# 高级感构图关键词库（明确区分）
COMPOSITION_STYLES = [
    {
        "composition": "三分法构图",
        "description": "三分法构图，主体放在三分线上，视觉焦点清晰，画面平衡感强",
        "unique_marker": "rule_of_thirds"
    },
    {
        "composition": "留白构图",
        "description": "留白构图，适当留白，不拥挤，增强画面呼吸感，突出主体",
        "unique_marker": "negative_space"
    },
    {
        "composition": "中心构图",
        "description": "中心构图，主体居中，对称平衡，视觉冲击力强，突出商品",
        "unique_marker": "center_composition"
    },
    {
        "composition": "对角线构图",
        "description": "对角线构图，主体沿对角线分布，动态感强，视觉引导自然",
        "unique_marker": "diagonal_composition"
    },
]

# 高级感色彩关键词库（明确区分）
COLOR_STYLES = [
    {
        "color": "暖色调",
        "description": "暖色调，色温自然，色彩过渡柔和，色调统一，温馨舒适",
        "unique_marker": "warm_tone"
    },
    {
        "color": "莫兰迪色系",
        "description": "莫兰迪色系，色彩低饱和度，质感高级不艳俗，色彩柔和耐看",
        "unique_marker": "morandi_palette"
    },
    {
        "color": "自然色",
        "description": "自然色，真实还原，肤色自然，商品色彩准确，真实感强",
        "unique_marker": "natural_color"
    },
    {
        "color": "电影调色",
        "description": "电影调色，色彩有层次，对比适中，氛围感强，高级质感",
        "unique_marker": "cinematic_color"
    },
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
    为4张图片分别增强提示词，确保多样性、真实体验、表情丰富、光影真实、高级感强、人脸一致
    
    Args:
        prompt: 原始提示词
        index: 图片索引（0-3）
        scene: 统一场景描述
    
    Returns:
        增强后的提示词
    """
    # 选择该图片的场景配置（多样性优先 + 明确区分）
    scene_config = FOUR_SHOT_SCENES[index]
    
    # 选择光线风格（真实光影 + 明确区分）
    lighting = LIGHTING_STYLES[index % len(LIGHTING_STYLES)]
    
    # 选择构图风格（高级感 + 明确区分）
    composition = COMPOSITION_STYLES[index % len(COMPOSITION_STYLES)]
    
    # 选择色彩风格（高级感 + 明确区分）
    color = COLOR_STYLES[index % len(COLOR_STYLES)]
    
    # 选择表情（多样性 + 明确区分）
    expression = EXPRESSIONS[index % len(EXPRESSIONS)]
    
    # 选择动作（多样性 + 明确区分）
    action = ACTION_STYLES[index % len(ACTION_STYLES)]
    
    # 选择使用环境（多样性）
    environment = random.choice(USE_ENVIRONMENTS)
    
    # 选择真实感增强（2-3个）
    selected_realism = random.sample(REALISM_ENHANCERS, random.randint(2, 3))
    
    # 构建完整描述 - 突出使用体验、真实光影、高级感和多样性
    enhanced_prompt_parts = [
        f"{scene}，{environment}",
        f"{scene_config['description']}，{scene_config['shot_type']}，{scene_config['angle']}，{scene_config['unique_marker']}",
        f"{expression['description']}，{action['description']}",
        f"{lighting['description']}，{lighting['unique_marker']}",
        f"{composition['description']}，{composition['unique_marker']}",
        f"{color['description']}，{color['unique_marker']}",
        f"{' '.join(selected_realism)}",
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
    if len(enhanced_prompt) > 800:
        enhanced_prompt = enhanced_prompt[:800]
    
    return enhanced_prompt


@tool
def generate_marketing_image(prompt: str, user_photo_url: str, product_photo_url: str, runtime: ToolRuntime=None) -> str:
    """
    一次性生成4张多样化场景、不同角度、人脸一致的社交媒体营销图片
    突出用户使用商品的体验，表情丰富，场景多样，人脸保持一致
    
    Args:
        prompt: 图片生成提示词，描述想要的风格和效果
        user_photo_url: 用户照片的URL（作为人脸参考）
        product_photo_url: 商品照片的URL
        runtime: 工具运行时上下文
    
    Returns:
        生成的4张图片URL，用换行符分隔
    """
    ctx = new_context(method="generate_marketing_image")
    
    client = ImageGenerationClient(ctx=ctx)
    
    # 随机选择一个基础场景
    scene = random.choice(SCENE_STYLES)
    
    # 为4张图片分别生成提示词（多样性优先 + 人脸一致性）
    image_urls = []
    
    for i in range(4):
        # 增强提示词 - 每张图片都有不同的体验和表情，但人脸保持一致
        enhanced_prompt = enhance_prompt_for_realism(prompt, i, scene)
        
        # 添加人脸一致性保障
        face_consistency_prompt = "保持人脸特征一致，相同的发型、五官特征、面部轮廓，相同的脸部识别特征"
        
        # 合并完整提示词
        full_prompt = f"{enhanced_prompt}，{face_consistency_prompt}"
        
        try:
            # 生成单张图片，始终使用用户照片作为人脸参考
            response = client.generate(
                prompt=full_prompt,
                image=[user_photo_url, product_photo_url],  # 用户照片作为第一张参考，确保人脸一致
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
