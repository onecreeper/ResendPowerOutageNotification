FROM python:3.9-slim

# 使用国内镜像源加速构建（先确保sources.list存在）
RUN echo "deb http://mirrors.aliyun.com/debian/ bullseye main" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian/ bullseye-updates main" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security bullseye-security main" >> /etc/apt/sources.list

# 安装最小必要的依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping && \
    pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ resend && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./app /app

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
