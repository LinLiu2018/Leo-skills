FROM node:22-alpine

# 安装依赖
RUN apk add --no-cache python3 git

# 安装 OpenClaw
RUN npm install -g openclaw@latest

# 创建工作目录
WORKDIR /app

# 暴露端口
EXPOSE 18789 18788 18790

# 启动命令
CMD ["openclaw", "gateway", "--port", "18789"]
