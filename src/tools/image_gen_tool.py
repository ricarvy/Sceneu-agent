"""
图片生成工具
支持图生图功能，将用户照片与商品照片合成为营销图片
"""
import random
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import ImageGenerationClient
from coze_coding_utils.runtime_ctx.context import new_context


# 真实感增强关键词库
REALISM_ENHANCERS = [
    # 质感相关
    "真实质感", "自然肤色", "适度后期", "保留纹理",
    "不过度美化", "自然过渡", "真实细节", "生活气息",
]

# 拍摄角度关键词库
SHOT_ANGLES = [
    "45度侧拍构图", "自然俯拍视角", "微微仰拍角度", "侧面轮廓展现",
    "斜角动态构图", "过肩镜头视角", "第一人称手持", "中景自然构图",
    "适当俯视突出商品", "立体侧拍", "自然角度", "真实拍摄视角",
]

# 光线质感关键词库
LIGHTING_STYLES = [
    "自然窗边散射光", "温暖午后自然光", "柔和室内环境光", "真实环境光",
    "适度光影层次", "自然阴影", "不过度曝光", "真实色温",
]


def enhance_prompt_for_realism(prompt: str) -> str:
    """
    增强提示词，增加真实感和拍摄角度描述
    
    Args:
        prompt: 原始提示词
    
    Returns:
        增强后的提示词
    """
    # 随机选择一些增强关键词
    selected_realism = random.sample(REALISM_ENHANCERS, 2)
    selected_angle = random.choice(SHOT_ANGLES)
    selected_lighting = random.choice(LIGHTING_STYLES)
    
    # 构建增强描述
    enhancement = f" {selected_angle}，{selected_lighting}，" + "，".join(selected_realism)
    
    # 检查原始提示词是否已经包含这些关键词，避免重复
    if not any(keyword in prompt for keyword in REALISM_ENHANCERS):
        enhanced_prompt = prompt + enhancement
    else:
        # 如果已经包含真实感关键词，只添加拍摄角度
        if not any(keyword in prompt for keyword in SHOT_ANGLES):
            enhanced_prompt = prompt + f" {selected_angle}"
        else:
            enhanced_prompt = prompt
    
    # 确保提示词不过长（最多保留前500个字符）
    if len(enhanced_prompt) > 500:
        enhanced_prompt = enhanced_prompt[:500]
    
    return enhanced_prompt


@tool
def generate_marketing_image(prompt: str, user_photo_url: str, product_photo_url: str, runtime: ToolRuntime=None) -> str:
    """
    生成社交媒体营销图片，将用户照片与商品照片合成
    
    Args:
        prompt: 图片生成提示词，描述想要的风格和效果
        user_photo_url: 用户照片的URL
        product_photo_url: 商品照片的URL
        runtime: 工具运行时上下文
    
    Returns:
        生成的图片URL
    """
    ctx = new_context(method="generate_marketing_image")
    
    client = ImageGenerationClient(ctx=ctx)
    
    # 增强提示词，增加真实感和拍摄角度描述
    enhanced_prompt = enhance_prompt_for_realism(prompt)
    
    # 使用两张参考图片进行图生图生成
    response = client.generate(
        prompt=enhanced_prompt,
        image=[user_photo_url, product_photo_url],
        size="2K",
        watermark=False,  # 营销图片不需要水印
        response_format="url"
    )
    
    if response.success:
        return response.image_urls[0]
    else:
        error_msg = ", ".join(response.error_messages) if response.error_messages else "Unknown error"
        # 检查是否是无效参数错误（可能是图片URL无效）
        if "InvalidParameter" in error_msg or "Bad Request" in error_msg:
            return f"图片生成失败：提供的图片URL无效或无法访问。请确保：\n1. 图片URL是公开可访问的有效链接\n2. URL以 http:// 或 https:// 开头\n3. 图片文件存在且可正常访问\n4. 不要使用 example.com 等测试用的假链接\n\n详细错误：{error_msg}"
        return f"图片生成失败: {error_msg}"
