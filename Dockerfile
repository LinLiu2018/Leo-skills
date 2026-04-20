# Leo AI System Dockerfile
# 优化版 - 多阶段构建

# ===== 阶段1: 构建 =====
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装构建依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ===== 阶段2: 运行 =====
FROM python:3.11-slim

WORKDIR /app

# 创建非root用户
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app

# 复制依赖
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# 复制应用代码
COPY --chown=appuser:appuser . .

# 环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV LEO_WORKSPACE=/app

# 暴露端口
EXPOSE 8080 18789

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# 切换到非root用户
USER appuser

# 默认命令
CMD ["python", "-m", "leo_gateway.gateway"]
