"""
图片生成工具
支持图生图功能，将用户照片与商品照片（支持单个或多个商品）合成为营销图片
支持一次性生成4张同一场景下不同pose和表情的图片
突出用户使用商品的体验和多样性
支持智能商品识别和组合匹配
支持用户上传场景图（如果上传，所有图片都符合此场景）
生成9:16比例图片
强化脸部细节刻画
降低AI感，保持真实自然
"""
import random
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import ImageGenerationClient
from coze_coding_utils.runtime_ctx.context import new_context


# 真实感增强关键词库（降低AI感 + 真实自然）
REALISM_ENHANCERS = [
    # 真实感相关（降低AI感）
    "像真人照片拍摄", "真实质感", "自然肤色", "轻度后期", "保留皮肤纹理",
    "生活化", "自然过渡", "真实细节", "生活气息", "像专业摄影师拍摄",
    "避免过度AI化", "避免过度美化", "避免过度修饰", "保持真实感",
    
    # 人物互动相关
    "人物自然使用商品", "手部自然接触", "眼神自然交流", "表情与使用场景自然协调",
    "自然握持", "真实互动", "自然使用状态", "自然展示状态", "享受体验",
    
    # 多商品互动相关
    "多个商品自然搭配", "不显拥挤", "主要商品重点展示", "次要商品辅助展示",
    
    # 降低AI感
    "皮肤有自然纹理和毛孔", "面部有自然的阴影和细节", "头发有自然的质感",
    "整体画面真实自然，不虚假", "色彩真实，不过度饱和", "光影真实，不过度夸张",
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

# 人脸一致性关键词库（高度一致 + 自然真实 + 降低AI感）
FACE_CONSISTENCY = [
    # 基础一致性
    "严格保持人脸特征，与原图人脸高度一致，必须能看出是同一个人",
    "保持原照片的发型、头发颜色、发型细节",
    "保持原照片的五官位置和相对比例，眼睛形状、大小、眼距",
    "保持原照片的脸型轮廓，下巴形状、颧骨位置",
    "保持原照片的鼻子特征，鼻梁高低、鼻翼大小、鼻头形状",
    "保持原照片的嘴巴特征，嘴唇厚薄、嘴型、嘴角形状",
    "保持原照片的眉毛形状和位置",
    "保持原照片的肤色特征，仅允许极轻微的自然调色",
    
    # 自然真实感（降低AI感）
    "像真人照片，避免过度AI化效果",
    "保持皮肤的天然质感，保留自然的纹理和毛孔",
    "脸型保持自然，不要过度液化或变形",
    "眼睛保持自然大小，不要过度放大或改变形状",
    "鼻子保持自然形状，不要过度修饰",
    "嘴巴保持自然形状，不要过度塑形",
    "肤色保持自然真实，不要过度美白或改变色温",
    "发际线保持自然，不要过度修饰",
    "面部阴影自然真实，不要过度去除",
    
    # 禁止过度处理
    "禁止过度磨皮，皮肤不能像塑料一样光滑",
    "禁止过度液化，不能改变脸型或五官位置",
    "禁止过度美白，肤色不能失真",
    "禁止过度修饰，保持原有的人物特征",
    "禁止过度美化，保持真实感",
    
    # 细节刻画
    "眼睛细节清晰自然，眼白有血丝自然痕迹，瞳孔真实反光",
    "鼻子细节自然立体，鼻梁有自然的高低起伏",
    "嘴巴细节自然真实，嘴唇有自然纹理",
    "皮肤质感真实，有自然的细小纹理和毛孔",
    "面部表情自然流畅，不要僵硬或过度夸张",
    
    # 整体一致性
    "4张图片的人脸必须高度一致，像同一个人在不同pose和表情下的照片",
    "人脸角度可以略有不同，但五官特征必须一致",
    "表情可以不同，但面部结构必须一致",
    "气质风格保持一致，不要出现不同风格的混合",
]

# 场景关键词库（多样化场景）
SCENE_STYLES = [
    "温馨咖啡馆午后场景", "办公室工位一角", "客厅沙发休息区", 
    "阳台阳光区", "卧室床头", "餐厅餐桌旁",
    "户外公园长椅", "书店阅读区", "地铁站通勤中",
]

# 4张图片的拍照姿势配置（同一场景下，不同pose）
FOUR_SHOT_POSES = [
    {
        "name": "站立展示",
        "pose_description": "自然站立姿态，身体略侧向镜头约15度，双脚自然分开与肩同宽，一手自然下垂，一手轻触或手持商品，姿态优雅自然",
        "camera_position": "相机水平，构图舒适",
        "focus": "展示商品的整体效果和个人气质",
        "unique_marker": "standing_pose"
    },
    {
        "name": "坐姿体验",
        "pose_description": "自然坐姿，身体前倾约20度，双手配合使用商品或放在桌面上，表情专注享受，姿态轻松舒适",
        "camera_position": "相机略微俯视约10度，构图自然",
        "focus": "展现商品在实际使用场景中的体验感",
        "unique_marker": "sitting_pose"
    },
    {
        "name": "侧身展示",
        "pose_description": "侧身约45度面向镜头，身体姿态舒展，一手举商品展示，另一手自然摆放在身侧，姿态优雅动感",
        "camera_position": "相机水平，构图有动感",
        "focus": "展示商品的侧面细节和个人曲线",
        "unique_marker": "side_pose"
    },
    {
        "name": "特写互动",
        "pose_description": "半身构图，双手操作或展示商品细节，身体略前倾，表情专注或愉悦，姿态真实自然",
        "camera_position": "相机水平，构图紧凑",
        "focus": "展现商品细节和手部操作的互动感",
        "unique_marker": "closeup_pose"
    },
]

# 表情多样性库（自然真实 + 丰富多样 + 降低AI感）
EXPRESSIONS = [
    {
        "expression": "微笑满足",
        "description": "自然的微笑，嘴角上扬约10-15度，眼神柔和温暖，眉毛自然舒展，脸颊有轻微的微笑肌，表情满足愉悦，像在享受美好体验",
        "unique_marker": "smiling_satisfied"
    },
    {
        "expression": "专注认真",
        "description": "眼神专注自然，眼睛微微睁大，眉毛自然聚拢，嘴唇自然闭合，表情认真专注，像在认真体验商品",
        "unique_marker": "focused_serious"
    },
    {
        "expression": "放松惬意",
        "description": "完全放松的表情，眼神柔和自然，嘴角自然放松，表情松弛舒适，像在享受轻松的时光",
        "unique_marker": "relaxed_comfortable"
    },
    {
        "expression": "自信大方",
        "description": "自然的自信，眼神明亮温和，下巴自然舒展，嘴角微微上扬约10度，表情自信大方，像在展示自己的选择",
        "unique_marker": "confident_natural"
    },
    {
        "expression": "开心愉悦",
        "description": "自然的笑容，眼睛有笑意，嘴角上扬约20-25度，表情开心愉悦，像遇到开心的事情",
        "unique_marker": "happy_natural"
    },
    {
        "expression": "好奇探索",
        "description": "好奇的表情，眼神游移自然，眉毛自然挑起，表情好奇有趣，像在探索新事物",
        "unique_marker": "curious_exploring"
    },
    {
        "expression": "温和亲切",
        "description": "温和的表情，眼神温柔，嘴角自然放松，表情亲切友好，像与朋友分享",
        "unique_marker": "gentle_friendly"
    },
    {
        "expression": "认真思考",
        "description": "认真思考的表情，眼神思考，眉毛自然皱起，表情认真有深度，像在认真考虑",
        "unique_marker": "thoughtful_serious"
    },
    {
        "expression": "平静自然",
        "description": "平静自然的表情，眼神平和，嘴角自然，表情平静放松，像在日常状态",
        "unique_marker": "calm_natural"
    },
    {
        "expression": "欣赏赞赏",
        "description": "欣赏的表情，眼神赞赏，嘴角自然上扬约15度，表情欣赏认可，像在欣赏美好的事物",
        "unique_marker": "appreciative_approving"
    },
]

# 使用动作多样性库（自然pose + 丰富多样 + 支持多商品）
ACTION_STYLES = [
    {
        "action": "自然手持",
        "description": "自然手持商品，姿态放松，手势自然大方，商品在手中位置合适，动作流畅自然",
        "unique_marker": "holding_natural"
    },
    {
        "action": "正在使用",
        "description": "自然地使用商品，动作协调流畅，展示商品的实际使用方式，姿态真实自然",
        "unique_marker": "using_natural"
    },
    {
        "action": "整理调整",
        "description": "自然地整理或调整商品，手指动作精细自然，表情专注认真，姿态放松舒适",
        "unique_marker": "adjusting_natural"
    },
    {
        "action": "展示分享",
        "description": "自然地展示商品，一手托举，另一手轻触，姿态优雅大方，手势自然真实",
        "unique_marker": "displaying_natural"
    },
    {
        "action": "搭配展示",
        "description": "展示商品与整体造型的搭配，身体姿态自然优雅，突出商品和整体效果的和谐",
        "unique_marker": "matching_natural"
    },
    {
        "action": "佩戴展示",
        "description": "自然地佩戴配饰，配饰位置合适自然，姿态舒适放松，展示配饰的搭配效果",
        "unique_marker": "wearing_natural"
    },
    {
        "action": "体验感受",
        "description": "体验商品的感受，身体放松，姿态舒适，表情满足，展现商品带来的美好体验",
        "unique_marker": "experiencing_natural"
    },
    {
        "action": "日常状态",
        "description": "以日常自然的状态使用商品，姿态舒适放松，动作流畅自然，展现商品在生活中的实用性",
        "unique_marker": "daily_state"
    },
    {
        "action": "站立展示",
        "description": "自然站立姿态，身体略侧向镜头，一手下垂一手持商品，姿态优雅舒展",
        "unique_marker": "standing_natural"
    },
    {
        "action": "坐姿体验",
        "description": "自然坐姿，身体前倾，双手配合使用商品，姿态放松舒适，体验感强",
        "unique_marker": "sitting_natural"
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
    "use_suitable_pose": "使用合适的pose展示商品，避免文字/logo细节问题",
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


def enhance_prompt_for_realism(prompt: str, index: int, scene: str, product_count: int = 1, has_custom_scene: bool = False) -> str:
    """
    为4张图片分别增强提示词，确保同一场景下不同pose/表情的多样性、真实体验、降低AI感、人脸高度一致
    
    Args:
        prompt: 原始提示词
        index: 图片索引（0-3）
        scene: 统一场景描述
        product_count: 商品数量（1个或多个）
        has_custom_scene: 是否有用户自定义场景
    
    Returns:
        增强后的提示词
    """
    # 选择该图片的拍照姿势（不同pose，同一场景）
    pose_config = FOUR_SHOT_POSES[index]
    
    # 选择光线风格（真实光影 + 自然真实）
    lighting = LIGHTING_STYLES[index % len(LIGHTING_STYLES)]
    
    # 选择构图风格（自然真实）
    composition = COMPOSITION_STYLES[index % len(COMPOSITION_STYLES)]
    
    # 选择色彩风格（自然真实）
    color = COLOR_STYLES[index % len(COLOR_STYLES)]
    
    # 选择表情（多样性 + 自然真实）
    expression = EXPRESSIONS[index % len(EXPRESSIONS)]
    
    # 选择动作（多样性 + 自然真实 + 支持多商品）
    if product_count > 1:
        # 多商品时选择支持搭配的动作
        multi_product_actions = [a for a in ACTION_STYLES if a['unique_marker'] in ['matching_natural', 'wearing_natural', 'displaying_natural']]
        action = multi_product_actions[index % len(multi_product_actions)]
    else:
        action = ACTION_STYLES[index % len(ACTION_STYLES)]
    
    # 选择使用环境（多样性）
    environment = random.choice(USE_ENVIRONMENTS)
    
    # 选择背景融合（2-3个）
    selected_fusion = random.sample(BACKGROUND_FUSION, random.randint(2, 3))
    
    # 选择真实感增强（2-3个，强调降低AI感）
    selected_realism = random.sample(REALISM_ENHANCERS, random.randint(2, 3))
    
    # 构建完整描述 - 突出pose多样性、表情多样性、真实体验、降低AI感、人脸一致性、背景自然融合
    enhanced_prompt_parts = [
        f"{scene}，{environment}" if not has_custom_scene else f"{scene}",
        f"{pose_config['pose_description']}，{pose_config['camera_position']}",
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
def generate_marketing_image(prompt: str, user_photo_url: str, product_photo_url: str, scene_photo_url: str = "", runtime: ToolRuntime=None) -> str:
    """
    一次性生成4张同一场景下不同pose和表情的社交媒体营销图片
    支持单个商品或多个商品组合（多个商品URL用逗号分隔）
    支持用户上传场景图（如果上传，所有图片都符合用户指定的场景）
    4张图片保持同一场景（用户指定场景或AI根据服饰搭配自动生成），但在不同拍照姿势和表情下展现
    人脸保持高度一致和自然真实，降低AI感，避免过度美化
    突出用户使用商品的体验，表情丰富自然，pose多样自然，光影真实自然，背景与人物自然融合
    智能识别商品类型，匹配合适的组合方式和场景
    生成9:16比例图片，强化脸部细节刻画
    
    Args:
        prompt: 图片生成提示词，描述想要的风格和效果
        user_photo_url: 用户照片的URL（作为人脸参考，必须高度一致）
        product_photo_url: 商品照片的URL，支持单个商品或多个商品（多个商品用逗号分隔，例如：url1,url2,url3）
        scene_photo_url: 场景照片的URL（可选，如果上传，所有图片都符合此场景）
        runtime: 工具运行时上下文
    
    Returns:
        生成的4张图片URL，用换行符分隔
    """
    ctx = new_context(method="generate_marketing_image")
    
    client = ImageGenerationClient(ctx=ctx)
    
    # 解析商品照片URL（支持单个或多个）
    product_urls = [url.strip() for url in product_photo_url.split(',') if url.strip()]
    product_count = len(product_urls)
    
    # 检查是否有自定义场景
    has_custom_scene = bool(scene_photo_url and scene_photo_url.strip())
    
    # 随机选择一个基础场景（如果没有自定义场景）
    if has_custom_scene:
        scene = "用户指定的场景"
    else:
        scene = random.choice(SCENE_STYLES)
    
    # 为4张图片分别生成提示词（多样性优先 + 人脸高度一致 + 背景自然融合 + 多商品展示 + 脸部细节精细）
    image_urls = []
    
    # 选择人脸一致性强化词（随机3-4个，强化脸部细节）
    selected_face_consistency = random.sample(FACE_CONSISTENCY, random.randint(3, 4))
    face_consistency_prompt = "，".join(selected_face_consistency)
    
    for i in range(4):
        # 增强提示词 - 每张图片都有不同的体验和表情，但人脸保持高度一致，背景自然融合，多商品合理展示，脸部细节精细
        enhanced_prompt = enhance_prompt_for_realism(prompt, i, scene, product_count, has_custom_scene)
        
        # 合并完整提示词（包含人脸一致性和背景融合）
        full_prompt = f"{enhanced_prompt}，{face_consistency_prompt}"
        
        try:
            # 生成单张图片，始终使用用户照片作为人脸参考（确保高度一致）
            # 如果有自定义场景，将场景图也作为参考图
            reference_images = [user_photo_url] + product_urls
            if has_custom_scene:
                reference_images.append(scene_photo_url)
            
            response = client.generate(
                prompt=full_prompt,
                image=reference_images,  # 用户照片、所有商品照片、场景图（如果有）作为参考
                size="1080x1920",  # 9:16比例
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
