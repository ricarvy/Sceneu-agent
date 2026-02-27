# 项目结构说明

# 本地运行
## 运行流程
bash scripts/local_run.sh -m flow

## 运行节点
bash scripts/local_run.sh -m node -n node_name

# 启动HTTP服务
bash scripts/http_run.sh -m http -p 5000

# 社交媒体营销图片生成器 - Web UI

本项目提供了一个完整的 Web UI 界面，用于社交媒体营销图片的生成。

## 📁 Web UI 文件
- `test_ui.html` - 演示版界面（静态页面，仅展示界面效果）
- `test_ui_connected.html` - 完整版界面（连接后端 API）
- `api_example.py` - FastAPI 后端服务示例
- `WEB_UI_README.md` - Web UI 详细使用指南

## 🚀 快速开始

### 1. 启动后端服务
```bash
# 安装依赖（如果还没安装）
pip install fastapi uvicorn python-multipart

# 启动 API 服务
python api_example.py

# 或者使用 uvicorn
uvicorn api_example:app --reload --host 0.0.0.0 --port 8000
```

### 2. 打开前端界面
用浏览器打开 `test_ui_connected.html` 文件。

### 3. 使用界面
1. 配置 API 地址（默认：http://localhost:8000）
2. 上传用户照片和商品照片
3. 输入或选择风格提示词
4. 点击"生成营销图片"按钮
5. 等待并查看生成结果

## 📖 详细文档
查看 `WEB_UI_README.md` 获取更多详细的使用说明和配置指南。


