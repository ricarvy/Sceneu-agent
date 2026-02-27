"""
社交媒体营销图片生成 - FastAPI 后端示例
展示如何创建一个完整的 Web API 来处理文件上传和图片生成
"""
import os
import io
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入 Agent
from agents.agent import build_agent

# 导入对象存储
from coze_coding_dev_sdk.s3 import S3SyncStorage

# 初始化 FastAPI
app = FastAPI(
    title="社交媒体营销图片生成 API",
    description="上传用户照片和商品照片，生成符合商品调性的营销图片",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化对象存储
storage = S3SyncStorage(
    endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
    access_key="",
    secret_key="",
    bucket_name=os.getenv("COZE_BUCKET_NAME"),
    region="cn-beijing",
)

# 初始化 Agent (全局复用，避免重复创建)
agent_instance = None

def get_agent():
    """获取或创建 Agent 实例"""
    global agent_instance
    if agent_instance is None:
        agent_instance = build_agent()
    return agent_instance


class GenerateRequest(BaseModel):
    """生成请求的模型（可选，用于 JSON 请求）"""
    user_photo_url: str
    product_photo_url: str
    prompt: str


class GenerateResponse(BaseModel):
    """生成响应的模型"""
    success: bool
    message: str
    result_url: Optional[str] = None
    error: Optional[str] = None


def upload_image_to_storage(file: UploadFile, prefix: str = "marketing") -> str:
    """
    将上传的图片保存到对象存储
    
    Args:
        file: 上传的文件对象
        prefix: 存储前缀路径
    
    Returns:
        图片的签名 URL
    """
    try:
        # 读取文件内容
        content = file.file.read()
        
        # 构建 文件名（确保符合命名规范）
        # 文件名规范：仅允许字母、数字、点、下划线、短横
        import re
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename or "image")
        
        # 上传到对象存储
        file_key = storage.upload_file(
            file_content=content,
            file_name=f"{prefix}/{safe_name}",
            content_type=file.content_type or "image/jpeg",
        )
        
        # 生成签名 URL（有效期 24 小时）
        signed_url = storage.generate_presigned_url(
            key=file_key,
            expire_time=86400,  # 24 小时
        )
        
        return signed_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")


@app.get("/")
async def root():
    """根路径，返回 API 信息"""
    return {
        "name": "社交媒体营销图片生成 API",
        "version": "1.0.0",
        "endpoints": {
            "POST /generate": "上传图片并生成营销图片",
            "POST /generate-from-urls": "通过图片 URL 生成营销图片",
            "GET /health": "健康检查",
        }
    }


@app.get("/health")
async def health():
    """健康检查接口"""
    return {"status": "healthy", "service": "marketing-image-generator"}


@app.post("/generate", response_model=GenerateResponse)
async def generate_marketing_image(
    user_photo: UploadFile = File(..., description="用户照片"),
    product_photo: UploadFile = File(..., description="商品照片"),
    prompt: str = Form(..., description="风格提示词"),
):
    """
    上传用户照片和商品照片，生成营销图片
    
    Args:
        user_photo: 用户照片文件
        product_photo: 商品照片文件
        prompt: 风格提示词
    
    Returns:
        生成结果，包含图片 URL
    """
    try:
        # 1. 上传图片到对象存储
        print(f"正在上传用户照片: {user_photo.filename}")
        user_photo_url = upload_image_to_storage(user_photo, "user_photos")
        
        print(f"正在上传商品照片: {product_photo.filename}")
        product_photo_url = upload_image_to_storage(product_photo, "product_photos")
        
        # 2. 构建发送给 Agent 的消息
        user_message = f"""
        请帮我生成一张营销图片。这是我的照片URL：{user_photo_url}
        这是商品照片URL：{product_photo_url}
        我想要的风格是："{prompt}"
        
        请按照你的标准流程生成图片，并返回创作思路、生成图片和使用建议。
        """
        
        # 3. 调用 Agent
        agent = get_agent()
        
        print("正在调用 Agent 生成图片...")
        # 注意：这里需要根据实际的 Agent 调用方式调整
        # 这是一个示例，实际实现取决于你的 Agent 接口
        
        # 模拟 Agent 响应（实际使用时替换为真实的 Agent 调用）
        result = {
            "success": True,
            "message": "图片生成成功",
            "result_url": user_photo_url,  # 示例返回，实际应该是生成的图片 URL
        }
        
        return GenerateResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"生成失败: {str(e)}")
        return GenerateResponse(
            success=False,
            message="生成失败",
            error=str(e)
        )


@app.post("/generate-from-urls", response_model=GenerateResponse)
async def generate_from_urls(request: GenerateRequest):
    """
    通过已有的图片 URL 生成营销图片（无需重新上传）
    
    Args:
        request: 包含图片 URL 和提示词的请求
    
    Returns:
        生成结果，包含图片 URL
    """
    try:
        # 构建发送给 Agent 的消息
        user_message = f"""
        请帮我生成一张营销图片。这是我的照片URL：{request.user_photo_url}
        这是商品照片URL：{request.product_photo_url}
        我想要的风格是："{request.prompt}"
        
        请按照你的标准流程生成图片，并返回创作思路、生成图片和使用建议。
        """
        
        # 2. 调用 Agent
        agent = get_agent()
        
        print("正在调用 Agent 生成图片...")
        
        # 注意：这里需要根据实际的 Agent 调用方式调整
        # 这是一个示例，实际实现取决于你的 Agent 接口
        
        result = {
            "success": True,
            "message": "图片生成成功",
            "result_url": request.user_photo_url,  # 示例返回
        }
        
        return GenerateResponse(**result)
        
    except Exception as e:
        print(f"生成失败: {str(e)}")
        return GenerateResponse(
            success=False,
            message="生成失败",
            error=str(e)
        )


# 启动说明
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("社交媒体营销图片生成 API 服务")
    print("=" * 60)
    print()
    print("启动方式:")
    print("  python api_example.py")
    print()
    print("或者使用 uvicorn:")
    print("  uvicorn api_example:app --reload --host 0.0.0.0 --port 8000")
    print()
    print("API 文档:")
    print("  http://localhost:8000/docs")
    print()
    print("=" * 60)
    
    uvicorn.run(
        "api_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
