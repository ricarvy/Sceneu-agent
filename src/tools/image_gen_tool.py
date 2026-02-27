"""
图片生成工具
支持图生图功能，将用户照片与商品照片合成为营销图片
"""
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import ImageGenerationClient
from coze_coding_utils.runtime_ctx.context import new_context


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
    
    # 使用两张参考图片进行图生图生成
    response = client.generate(
        prompt=prompt,
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
