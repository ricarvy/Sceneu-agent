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
import os
import random
import re
from langchain.tools import tool
from typing import Optional, Tuple


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

# 站立姿势的轻微变化配置（同一场景下，站立姿势多样化）
STANDING_POSES = [
    {
        "name": "正面站立",
        "pose_description": "自然正面站立，身体正对镜头，双脚自然分开与肩同宽，一手自然下垂，一手轻触或手持商品，姿态优雅自然",
        "camera_position": "相机水平，构图舒适",
        "focus": "展示商品的整体效果和个人气质",
        "unique_marker": "standing_front"
    },
    {
        "name": "略侧站立",
        "pose_description": "自然站立，身体略侧向镜头约15度，双脚自然分开，一手轻触商品，一手自然下垂，姿态优雅",
        "camera_position": "相机水平，构图舒适",
        "focus": "展示商品效果和个人气质",
        "unique_marker": "standing_slight_side"
    },
    {
        "name": "手持展示",
        "pose_description": "自然站立，双手持商品展示给镜头，手势优雅，姿态大方",
        "camera_position": "相机水平，构图舒适",
        "focus": "展示商品细节",
        "unique_marker": "standing_holding"
    },
    {
        "name": "动态站立",
        "pose_description": "自然站立，身体略微前倾约5-10度，一手拿商品，一手摆动，姿态有动感",
        "camera_position": "相机水平，构图舒适",
        "focus": "展示商品效果和动态感",
        "unique_marker": "standing_dynamic"
    },
    {
        "name": "轻松站立",
        "pose_description": "自然站立，身体放松，一手插兜，一手轻触商品，姿态轻松",
        "camera_position": "相机水平，构图舒适",
        "focus": "展示商品效果和轻松感",
        "unique_marker": "standing_relaxed"
    },
    {
        "name": "优雅站立",
        "pose_description": "自然站立，身体优雅舒展，一手轻扶商品，一手自然下垂，姿态优雅",
        "camera_position": "相机水平，构图舒适",
        "focus": "展示商品效果和优雅气质",
        "unique_marker": "standing_elegant"
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

PRODUCT_CATEGORY_PATTERNS: list[Tuple[str, str]] = [
    ("连衣裙|裙|半身裙|dress|skirt", "连衣裙/裙子"),
    ("上衣|衬衫|t恤|tee|sweatshirt|hoodie|shirt|top", "上衣"),
    ("外套|夹克|大衣|西装|coat|jacket|blazer|trench", "外套"),
    ("裤|牛仔裤|长裤|短裤|pants|jeans|trousers|shorts", "裤装"),
    ("鞋|靴|高跟|运动鞋|sneaker|heels|boots|shoes", "鞋子"),
    ("包|手提包|挎包|肩包|背包|bag|handbag|tote|backpack|crossbody", "包袋"),
    ("眼镜|墨镜|太阳镜|glasses|sunglasses", "眼镜"),
    ("手表|watch", "手表"),
    ("帽|cap|hat|beanie", "帽子"),
    ("项链|necklace", "项链"),
    ("耳环|earring", "耳环"),
    ("口红|lipstick", "口红"),
]

def infer_product_category(title: Optional[str], image_url: Optional[str]) -> Optional[str]:
    candidates: list[str] = []
    if title:
        candidates.append(title)
    if image_url:
        try:
            from urllib.parse import urlparse
            p = urlparse(image_url)
            candidates.append(p.path)
        except Exception:
            candidates.append(image_url)
    text = " ".join([c.lower() for c in candidates if c])
    for patt, cat in PRODUCT_CATEGORY_PATTERNS:
        try:
            import re
            if re.search(patt, text):
                return cat
        except Exception:
            if any(tok in text for tok in patt.split("|")):
                return cat
    return None

def extract_urls(text: Optional[str]) -> list[str]:
    if not text:
        return []
    t = text.replace("，", ",").replace("\n", " ").replace("\r", " ")
    t = t.replace("`", "").replace("“", "").replace("”", "").replace("‘", "").replace("’", "")
    urls = re.findall(r"https?://[^\s,]+", t)
    res = []
    for u in urls:
        u = u.strip().strip(" ,;)]}>\"'")
        if u.startswith("http"):
            res.append(u)
    if not res and ("," in t):
        parts = [p.strip() for p in t.split(",") if p.strip()]
        for p in parts:
            if p.startswith("http"):
                res.append(p)
    return res
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


def enhance_prompt_for_realism(prompt: str, scene: str, product_count: int = 1, has_custom_scene: bool = False) -> str:
    """
    为1张图片增强提示词，确保站立姿势多样化、表情自然、真实体验、降低AI感、人脸高度一致
    
    Args:
        prompt: 原始提示词
        scene: 场景描述
        product_count: 商品数量（1个或多个）
        has_custom_scene: 是否有用户自定义场景
    
    Returns:
        增强后的提示词
    """
    # 随机选择一个站立姿势（轻微变化）
    pose_config = random.choice(STANDING_POSES)
    
    # 随机选择光线风格（真实光影 + 自然真实）
    lighting = random.choice(LIGHTING_STYLES)
    
    # 随机选择构图风格（自然真实）
    composition = random.choice(COMPOSITION_STYLES)
    
    # 随机选择色彩风格（自然真实）
    color = random.choice(COLOR_STYLES)
    
    # 随机选择表情（自然真实）
    expression = random.choice(EXPRESSIONS)
    
    # 随机选择动作（多样性 + 自然真实 + 支持多商品）
    if product_count > 1:
        # 多商品时选择支持搭配的动作
        multi_product_actions = [a for a in ACTION_STYLES if a['unique_marker'] in ['matching_natural', 'wearing_natural', 'displaying_natural']]
        action = random.choice(multi_product_actions)
    else:
        action = random.choice(ACTION_STYLES)
    
    # 选择使用环境
    environment = random.choice(USE_ENVIRONMENTS)
    
    # 选择背景融合（2-3个）
    selected_fusion = random.sample(BACKGROUND_FUSION, random.randint(2, 3))
    
    # 选择真实感增强（2-3个，强调降低AI感）
    selected_realism = random.sample(REALISM_ENHANCERS, random.randint(2, 3))
    
    # 构建完整描述 - 突出pose多样性、表情自然、真实体验、降低AI感、人脸一致性、背景自然融合
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
def generate_marketing_image(
    user_photo_url: str,
    product_photo_url: str,
    prompt: str,
    product_title: str = None,
    scene_ref_url: str = None,
    mode: str = "inspire"
) -> str:
    """
    Generate a social media marketing image based on user photo and product photo.
    
    Args:
        user_photo_url: The URL of the user's photo.
        product_photo_url: The URL of the product photo (supports multiple products).
        prompt: The prompt describing the style and atmosphere.
        scene_ref_url: (Optional) The URL of a scene reference image.
        mode: (Optional) The generation mode. "copy" means maintaining the pose and scene of the user photo, only replacing the face and product. "inspire" means the AI is free to be creative (default).
    """
    base_prompt = f"{prompt}, 杰作, 8k分辨率, 极度详细, 专业摄影, 商业级光影"

    mode_prompt = ""
    if mode == "copy":
        mode_prompt = (
            "Keep the human pose, body structure, and background scene exactly the same as the user_photo_url. "
            "Only replace the face with the user's face (adding appropriate expression) "
            "and put the product on the person naturally (replace clothes/pants if product is clothing). "
            "Do not change the composition or background."
        )
    else:
        mode_prompt = (
            "Create a new creative scene and pose. "
            "The person should be using/wearing the product naturally. "
            "The facial features must match the user_photo_url. "
        )
        if scene_ref_url:
            mode_prompt += " The background and lighting style must strictly follow the scene_ref_url."

    product_urls_for_category = extract_urls(product_photo_url)
    
    # 支持多商品处理
    product_constraints = []
    
    # 检查是否包含多个商品标题（逗号分隔）
    is_multi_product = product_title and ("," in product_title or "，" in product_title)
    
    if is_multi_product:
        # 多商品逻辑
        titles = [t.strip() for t in re.split(r'[,，]', product_title) if t.strip()]
        
        # 记录每个商品的信息
        for i, title in enumerate(titles):
            # 尝试找到对应的图片URL（假设顺序对应）
            curr_url = product_urls_for_category[i] if i < len(product_urls_for_category) else None
            curr_category = infer_product_category(title, curr_url)
            
            product_constraints.append(f"商品{i+1}：{title}")
            if curr_category:
                product_constraints.append(f"（类别：{curr_category}）")
                
                # 添加类别特定的穿着/佩戴约束
                if curr_category in ["连衣裙/裙子", "上衣", "外套", "裤装"]:
                    product_constraints.append("- 需自然穿着在人物身上，贴合身体曲线")
                elif curr_category in ["包袋"]:
                    product_constraints.append("- 需自然肩背、手提或斜挎")
                elif curr_category in ["鞋子"]:
                    product_constraints.append("- 需穿在脚上")
                elif curr_category in ["眼镜"]:
                    product_constraints.append("- 需佩戴在脸部")
                elif curr_category in ["手表", "项链", "耳环", "帽子"]:
                    product_constraints.append("- 需佩戴在相应身体部位")
        
        product_constraints.append("请将上述所有商品自然组合在人物身上，确保搭配协调。")
        product_constraints.append("严禁自行添加未提到的其他商品。")
        
    else:
        # 单商品逻辑（原有逻辑优化）
        first_product_url_for_category = product_urls_for_category[0] if product_urls_for_category else None
        category = infer_product_category(product_title, first_product_url_for_category)
        
        if product_title:
            product_constraints.append(f"核心展示商品：{product_title}。")
            product_constraints.append(f"请严格基于商品标题“{product_title}”进行生成，不要自行发散或看图说话。")
            
        if category:
            product_constraints.append(f"商品类别：{category}。")
            if category in ["连衣裙/裙子", "上衣", "外套", "裤装"]:
                product_constraints.append("以穿着方式展示，衣物自然贴合身体。")
            elif category in ["包袋"]:
                product_constraints.append("以肩背/手提/斜挎方式自然展示。")
            elif category in ["鞋子"]:
                product_constraints.append("穿在脚上，步态自然。")
            elif category in ["眼镜"]:
                product_constraints.append("佩戴在脸部合适位置。")
            elif category in ["手表"]:
                product_constraints.append("佩戴在手腕上，松紧合适。")
            elif category in ["帽子"]:
                product_constraints.append("佩戴在头部恰当位置。")
            elif category in ["项链", "耳环"]:
                product_constraints.append("以佩戴方式展示，位置合理。")
            elif category in ["口红"]:
                product_constraints.append("以涂抹效果展示，唇色自然。")
        
        product_constraints.append("严格禁止出现多个不同商品或额外配饰，确保单一商品。")
        product_constraints.append("若商品图存在多件物品，仅选择与标题匹配的一件进行合成。")

    api_key = os.getenv("ARK_API_KEY") or os.getenv("COZE_INTEGRATION_MODEL_API_KEY")
    base_url = os.getenv("ARK_BASE_URL") or os.getenv("COZE_INTEGRATION_MODEL_BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3"
    model = os.getenv("ARK_IMAGE_MODEL") or os.getenv("COZE_INTEGRATION_IMAGE_MODEL") or "doubao-seedream-5-0-260128"
    size = os.getenv("ARK_IMAGE_SIZE") or "2K"
    response_format = os.getenv("ARK_IMAGE_RESPONSE_FORMAT") or "url"
    sequential_image_generation = os.getenv("ARK_IMAGE_SEQUENTIAL") or "disabled"
    stream = (os.getenv("ARK_IMAGE_STREAM") or "false").lower() == "true"
    watermark = (os.getenv("ARK_IMAGE_WATERMARK") or "true").lower() == "true"
    count_str = os.getenv("ARK_IMAGE_COUNT") or "4"
    try:
        k = max(1, min(8, int(count_str)))
    except:
        k = 4

    if not api_key:
        return "Failed to generate image: ARK_API_KEY is not set"

    try:
        from volcenginesdkarkruntime import Ark
    except Exception as e:
        return f"Failed to generate image: volcenginesdkarkruntime not installed ({str(e)})"

    try:
        client = Ark(base_url=base_url, api_key=api_key)
        product_urls: list[str] = extract_urls(product_photo_url)
        base_images: list[str] = []
        if user_photo_url and user_photo_url.startswith("http"):
            base_images.append(user_photo_url)
        base_images.extend([u for u in product_urls if u])
        if mode == "inspire" and scene_ref_url and scene_ref_url.startswith("http"):
            base_images.append(scene_ref_url)

        results: list[str] = []
        for _ in range(k):
            realism_prompt = ", ".join(random.sample(REALISM_ENHANCERS, 5))
            if mode == "copy":
                expr = random.choice(EXPRESSIONS)["description"]
                
                # 丰富动作库：分为手部、腿部、头部、身体四个维度，确保不改变整体构图和运镜
                hand_moves = ["单手轻微插兜", "抬手整理发梢", "双手自然下垂", "单手轻触脸颊", "手持随身小物"]
                leg_moves = ["重心微调", "双脚自然站立", "一脚微微前伸", "双腿交叉站立", "膝盖微屈"]
                head_moves = ["头部微侧", "下巴微扬", "平视镜头", "眼神略微看向侧方"]
                body_moves = ["身体正面朝向", "身体微侧15度", "肩膀自然放松"]
                
                # 随机组合动作
                micro = f"{random.choice(hand_moves)}，{random.choice(leg_moves)}，{random.choice(head_moves)}，{random.choice(body_moves)}"
                
                per_mode = (
                    "【严格运镜约束】镜头焦距、拍摄距离、相机机位、拍摄角度必须与用户原图完全一致。禁止拉近或推远镜头，禁止改变景别（如全身变半身）。"
                    "【背景与构图】背景环境、光影方向、画面构图结构保持不变。"
                    "【人物一致性】人物与用户图为同一人，五官与脸型高度一致。"
                    "【姿态丰富性】在保持原图整体站位和景别不变的前提下，允许人物进行自然的肢体微调（如手部、腿部、头部动作变化），增加生动感。"
                )
                per_prompt = f"{base_prompt}. {per_mode} {expr}，{micro}。{realism_prompt} " + " ".join(product_constraints)
                images = [u for u in base_images if u]
            else:
                per_prompt = f"{base_prompt}. {mode_prompt} {realism_prompt} " + " ".join(product_constraints)
                images = [u for u in base_images if u]

            from volcenginesdkarkruntime.types.images.images import SequentialImageGenerationOptions
            seq_mode = "auto" if k > 1 else "disabled"
            resp = client.images.generate(
                model=model,
                prompt=per_prompt,
                image=images or None,
                sequential_image_generation=seq_mode,
                sequential_image_generation_options=SequentialImageGenerationOptions(max_images=k),
                response_format=response_format,
                size=size,
                stream=False,
                watermark=watermark,
            )
            data = getattr(resp, "data", None)
            if data and len(data) > 0:
                urls = [getattr(item, "url", None) for item in data]
                for u in urls:
                    if u and u not in results:
                        results.append(u)
                        if len(results) >= k:
                            break
            if len(results) >= k:
                break
        if results:
            return "\n".join(results[:k])
        return "Failed to generate image: no image urls"
    except Exception as e:
        return f"Failed to generate image: {str(e)}"
