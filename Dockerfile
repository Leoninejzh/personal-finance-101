FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 安装基础依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件，利用镜像缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制其余所有代码（包含 app.py, i18n.py 等）
COPY . .

# 暴露 8080 端口（这是 Cloud Run 的标准）
EXPOSE 8080

# 启动命令：必须绑定到 0.0.0.0 和 8080 端口
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
