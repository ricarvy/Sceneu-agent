# 社交媒体营销图片生成器 - Web UI 使用指南

## 📁 文件说明

1. **test_ui.html** - 演示版界面（静态页面，仅展示界面效果）
2. **test_ui_connected.html** - 完整版界面（连接后端 API）
3. **api_example.py** - FastAPI 后端服务示例

## 🚀 快速开始

### 步骤 1: 启动后端服务

```bash
# 安装依赖（如果还没安装）
pip install fastapi uvicorn python-multipart

# 启动 API 服务
python api_example.py

# 或者使用 uvicorn
uvicorn api_example:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 步骤 2: 打开前端界面

用浏览器打开 `test_ui_connected.html` 文件。

### 步骤 3: 使用界面

1. **配置 API 地址**
   - 在页面顶部输入后端 API 地址
   - 默认：`http://localhost:8000`

2. **上传图片**
   - 点击或拖拽上传用户照片
   - 点击或拖拽上传商品照片

3. **输入提示词**
   - 手动输入风格描述
   - 或点击"快速选择风格"标签

4. **生成图片**
   - 点击"生成营销图片"按钮
   - 等待 AI 处理（约 10-30 秒）
   - 查看生成结果

## 🔧 后端 API 接口

### POST /generate
上传图片并生成营销图片

**请求方式:** `multipart/form-data`

**参数:**
- `user_photo` (file, 必填): 用户照片文件
- `product_photo` (file, 必填): 商品照片文件
- `prompt` (string, 必填): 风格提示词

**响应:**
```json
{
  "success": true,
  "message": "图片生成成功",
  "result_url": "https://..."
}
```

### POST /generate-from-urls
通过已有的图片 URL 生成营销图片

**请求方式:** `application/json`

**参数:**
```json
{
  "user_photo_url": "https://...",
  "product_photo_url": "https://...",
  "prompt": "高级感，自然光线"
}
```

**响应:** 同 `/generate`

### GET /health
健康检查接口

**响应:**
```json
{
  "status": "healthy",
  "service": "marketing-image-generator"
}
```

## 📋 注意事项

### 图片要求
- **格式:** JPG, PNG, GIF, WebP 等常见图片格式
- **大小:** 单张图片不超过 10MB
- **质量:** 建议选择清晰、光线良好的照片
- **内容:** 
  - 用户照片：建议人物姿态自然、表情自然
  - 商品照片：建议主体清晰、无遮挡、背景简洁

### 提示词技巧
- **简洁:** 2-10 个关键词即可，AI 会自动优化
- **风格描述:** 高级感、清新、复古、简约等
- **场景描述:** 户外、居家、办公室、咖啡馆等
- **光线:** 自然光、暖光、柔光等
- **色彩:** 暖色调、冷色调、低饱和度等

### 常见问题

**Q: 提示"请检查后端服务是否已启动"？**
A: 请确保已运行 `python api_example.py` 启动服务，并且 API 地址配置正确。

**Q: 图片上传失败？**
A: 检查图片格式和大小是否符合要求，确保网络连接正常。

**Q: 生成时间过长？**
A: 图片生成通常需要 10-30 秒，请耐心等待。如果超过 1 分钟仍未完成，请刷新页面重试。

**Q: 生成的图片效果不理想？**
A: 尝试：
- 使用更清晰、光线更好的原图
- 调整提示词，更精确地描述风格
- 检查用户照片和商品照片的风格是否协调

## 🎨 界面自定义

### 修改颜色主题
在 HTML 文件中查找以下颜色变量并修改：

```css
/* 渐变背景 */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* 主题色 */
border-color: #667eea;
background: #667eea;
```

### 修改快速选择风格标签
在 HTML 文件中查找 `<span class="example-tag"` 标签，修改 onclick 参数：

```html
<span class="example-tag" onclick="setPrompt('你的风格描述')">标签文本</span>
```

### 修改 API 默认地址
在 HTML 文件中查找：
```html
<input type="text" id="apiUrl" value="http://localhost:8000">
```
修改 `value` 属性为你的实际 API 地址。

## 📦 部署建议

### 本地开发
直接使用上述快速开始步骤即可。

### 生产部署

1. **后端部署**
```bash
# 使用 Gunicorn 部署 FastAPI
pip install gunicorn
gunicorn api_example:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

2. **前端部署**
- 将 `test_ui_connected.html` 部署到 Web 服务器
- 修改 API 地址为生产环境的实际地址
- 配置 HTTPS（生产环境推荐）

3. **反向代理配置（Nginx 示例）**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/html/files;
        index test_ui_connected.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🛠️ 技术栈

- **前端:** HTML5, CSS3, JavaScript (原生)
- **后端:** Python, FastAPI
- **存储:** S3 兼容对象存储
- **AI 模型:** 豆包多模态大模型

## 📞 支持

如有问题，请检查：
1. 后端服务日志
2. 浏览器控制台错误信息
3. 网络连接状态
