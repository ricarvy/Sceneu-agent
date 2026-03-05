# 使用官方 Python 3.11 镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，防止 Python 生成 .pyc 文件，并使输出无缓冲
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 替换为国内镜像源 (Debian) 并安装系统依赖
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装依赖 (使用国内 pip 源)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制项目代码
COPY . .

# 暴露端口 8888 (容器内部端口，外部映射为 8911)
EXPOSE 8888

# 启动命令
CMD ["./scripts/http_run.sh", "-p", "8888"]
