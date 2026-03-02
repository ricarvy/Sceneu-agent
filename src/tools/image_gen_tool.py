"""
图片生成工具
支持图生图功能，将用户照片与商品照片（支持单个或多个商品）合成为营销图片
支持一次性生成4张同一场景下不同角度的图片
突出用户使用商品的体验和多样性
支持智能商品识别和组合匹配
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
    # 多商品互动相关
    "多个商品自然搭配", "不显拥挤", "主要商品重点展示", "次要商品辅助展示",
]

# 背景融合关键词库（减少剥离感）
BACKGROUND_FUSION = [
    "人物与背景自然融合，边缘过渡自然，无生硬边界",
    "背景虚化自然渐进，景深过渡柔和，人物与背景光线一致",
    "人物阴影投射在背景上，增强立体感和融合感",
    "人物轮廓与背景自然融合，边缘羽毛化处理，避免剪贴感",
    "人物与背景色彩呼应，色调统一，避免色温不协调",
    "人物反光与环境光呼应，增强真实感",
]

# 人脸一致性关键词库（高度一致）
FACE_CONSISTENCY = [
    "严格保持人脸特征，与原图人脸高度一致，可轻微美颜但必须能看出是同一个人",
    "保持原照片的发型、五官位置、脸型轮廓、眼睛特征、鼻子特征、嘴巴特征",
    "人脸变形程度极小，仅允许轻微的角度调整，禁止大幅度改变人脸结构",
    "保持原照片的表情风格，仅调整表情细节（如微笑幅度），禁止改变表情基调",
    "保持原照片的肤色特征，仅允许轻微提亮或调色，禁止改变肤色本质",
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

# 表情多样性库（突出用户体验 + 高度一致 + 明确区分）
EXPRESSIONS = [
    {
        "expression": "微笑满足",
        "description": "温柔的微笑，嘴角上扬约15度，眼神柔和温暖，眉毛自然舒展，脸颊有轻微的微笑肌显现，表情满足愉悦，享受使用商品的美好体验",
        "unique_marker": "smiling_satisfied"
    },
    {
        "expression": "专注认真",
        "description": "眼神专注地注视商品，眼睛微微睁大，眉毛微微聚拢，嘴唇紧闭成思考状，表情认真严肃，沉浸在体验商品的功能和细节中",
        "unique_marker": "focused_serious"
    },
    {
        "expression": "惊喜愉悦",
        "description": "眼睛睁大，眼神发光，眉毛挑高，嘴巴张开约30度露出整齐牙齿，表情惊喜兴奋，发现商品意想不到的功能或效果",
        "unique_marker": "surprised_delighted"
    },
    {
        "expression": "放松自然",
        "description": "完全放松的表情，眼睛半睁半闭，眼神柔和懒散，嘴角自然下垂，嘴唇微张，表情松弛舒适，享受商品带来的放松体验",
        "unique_marker": "relaxed_natural"
    },
    {
        "expression": "自信优雅",
        "description": "自信的微笑，眼神坚定明亮，下巴微微抬起，嘴角上扬约20度，表情优雅大方，展现使用商品时的自信和优雅气质",
        "unique_marker": "confident_elegant"
    },
    {
        "expression": "开心愉悦",
        "description": "灿烂的笑容，眼睛弯成月牙状，嘴角上扬约40度露出牙齿，脸颊有明显的笑纹，表情开心快乐，对商品非常满意",
        "unique_marker": "happy_joyful"
    },
    {
        "expression": "思考探索",
        "description": "思考的表情，眼神游移探索，眉毛微微皱起，手指轻触下巴，表情好奇探索，正在探索商品的各种可能性",
        "unique_marker": "thinking_exploring"
    },
    {
        "expression": "满意肯定",
        "description": "满意的点头表情，眼神肯定赞赏，嘴角上扬约25度，头部微微点头，表情肯定认可，对商品的效果非常满意",
        "unique_marker": "satisfied_approval"
    },
]

# 使用动作多样性库（明确区分 + 丰富多样 + 支持多商品）
ACTION_STYLES = [
    {
        "action": "正在使用",
        "description": "人物正在使用商品的核心功能，双手协调操作商品，动作流畅自然流畅，展示商品的实际使用方式和使用过程",
        "unique_marker": "using_action"
    },
    {
        "action": "手持展示",
        "description": "人物手持商品展示给镜头，一手托举商品，另一手轻触商品细节，手势优雅大方，商品在画面中清晰可见",
        "unique_marker": "holding_display"
    },
    {
        "action": "调整细节",
        "description": "人物调整商品的细节设置，手指精细操作商品的控制区或调节按钮，表情专注，展示商品的可调节性和个性化功能",
        "unique_marker": "adjusting_action"
    },
    {
        "action": "享受体验",
        "description": "人物享受商品带来的体验，身体后仰放松，双手自然放置，姿态舒展舒适，表情满足，展现商品带来的愉悦感受",
        "unique_marker": "enjoying_action"
    },
    {
        "action": "穿搭展示",
        "description": "人物穿着服装类商品，展示穿搭效果，身体姿态自然优雅，突出服装的质感和设计细节",
        "unique_marker": "outfit_display"
    },
    {
        "action": "配饰搭配",
        "description": "人物佩戴配饰类商品（如挎包、首饰），展示配饰与整体造型的搭配效果，配饰位置自然合适",
        "unique_marker": "accessory_matching"
    },
    {
        "action": "完整造型",
        "description": "人物展示完整的商品组合造型，多个商品协调搭配，形成统一的整体形象，突出整体体验感",
        "unique_marker": "complete_look"
    },
    {
        "action": "日常出行",
        "description": "人物以日常出行的方式使用商品，步伐自然，姿态舒适，展现商品在日常生活中的实用性",
        "unique_marker": "daily_outing"
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


def enhance_prompt_for_realism(prompt: str, index: int, scene: str, product_count: int = 1) -> str:
    """
    为4张图片分别增强提示词，确保多样性、真实体验、表情丰富、光影真实、高级感强、人脸高度一致、背景自然融合、多商品合理展示
    
    Args:
        prompt: 原始提示词
        index: 图片索引（0-3）
        scene: 统一场景描述
        product_count: 商品数量（1个或多个）
    
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
    
    # 选择动作（多样性 + 明确区分 + 支持多商品）
    # 如果是多个商品，优先选择支持多商品的动作
    if product_count > 1:
        multi_product_actions = [a for a in ACTION_STYLES if a['unique_marker'] in ['outfit_display', 'accessory_matching', 'complete_look', 'daily_outing']]
        action = multi_product_actions[index % len(multi_product_actions)]
    else:
        action = ACTION_STYLES[index % len(ACTION_STYLES)]
    
    # 选择使用环境（多样性）
    environment = random.choice(USE_ENVIRONMENTS)
    
    # 选择背景融合（2-3个）
    selected_fusion = random.sample(BACKGROUND_FUSION, random.randint(2, 3))
    
    # 选择真实感增强（1-2个）
    selected_realism = random.sample(REALISM_ENHANCERS, random.randint(1, 2))
    
    # 构建完整描述 - 突出使用体验、真实光影、高级感、人脸一致性、背景融合和多商品展示
    enhanced_prompt_parts = [
        f"{scene}，{environment}",
        f"{scene_config['description']}，{scene_config['shot_type']}，{scene_config['angle']}，{scene_config['unique_marker']}",
        f"{expression['description']}，{action['description']}",
        f"{lighting['description']}，{lighting['unique_marker']}",
        f"{composition['description']}，{composition['unique_marker']}",
        f"{color['description']}，{color['unique_marker']}",
        f"{' '.join(selected_fusion)}",
        f"{' '.join(selected_realism)}",
    ]
    
    # 如果是多个商品，添加多商品相关的提示
    if product_count > 1:
        multi_product_prompts = [
            "多个商品自然搭配展示，形成完整造型",
            "主要商品重点展示，次要商品辅助展示",
            "商品之间风格协调统一，不显拥挤",
        ]
        enhanced_prompt_parts.append("，".join(multi_product_prompts))
    
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
    if len(enhanced_prompt) > 1000:
        enhanced_prompt = enhanced_prompt[:1000]
    
    return enhanced_prompt


@tool
def generate_marketing_image(prompt: str, user_photo_url: str, product_photo_url: str, runtime: ToolRuntime=None) -> str:
    """
    一次性生成4张多样化场景、不同角度、人脸高度一致、背景自然融合的社交媒体营销图片
    支持单个商品或多个商品组合（多个商品URL用逗号分隔）
    突出用户使用商品的体验，表情丰富，场景多样，人脸保持高度一致，背景与人物自然融合
    智能识别商品类型，匹配合适的组合方式和场景
    
    Args:
        prompt: 图片生成提示词，描述想要的风格和效果
        user_photo_url: 用户照片的URL（作为人脸参考，必须高度一致）
        product_photo_url: 商品照片的URL，支持单个商品或多个商品（多个商品用逗号分隔，例如：url1,url2,url3）
        runtime: 工具运行时上下文
    
    Returns:
        生成的4张图片URL，用换行符分隔
    """
    ctx = new_context(method="generate_marketing_image")
    
    client = ImageGenerationClient(ctx=ctx)
    
    # 解析商品照片URL（支持单个或多个）
    product_urls = [url.strip() for url in product_photo_url.split(',') if url.strip()]
    product_count = len(product_urls)
    
    # 随机选择一个基础场景
    scene = random.choice(SCENE_STYLES)
    
    # 为4张图片分别生成提示词（多样性优先 + 人脸高度一致 + 背景自然融合 + 多商品展示）
    image_urls = []
    
    # 选择人脸一致性强化词（随机2个）
    selected_face_consistency = random.sample(FACE_CONSISTENCY, 2)
    face_consistency_prompt = "，".join(selected_face_consistency)
    
    for i in range(4):
        # 增强提示词 - 每张图片都有不同的体验和表情，但人脸保持高度一致，背景自然融合，多商品合理展示
        enhanced_prompt = enhance_prompt_for_realism(prompt, i, scene, product_count)
        
        # 合并完整提示词（包含人脸一致性和背景融合）
        full_prompt = f"{enhanced_prompt}，{face_consistency_prompt}"
        
        try:
            # 生成单张图片，始终使用用户照片作为人脸参考（确保高度一致）
            # 如果是多个商品，将所有商品照片都作为参考图
            reference_images = [user_photo_url] + product_urls
            
            response = client.generate(
                prompt=full_prompt,
                image=reference_images,  # 用户照片和所有商品照片作为参考
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
