# 服务器监控系统

断电和网络状态监控，状态变化时自动发送邮件通知。

## 功能
- 断电检测和恢复通知
- 内网和外网连接监控
- 网络状态变化实时通知
- 自愈功能和稳定性保障

## 快速开始

1. **配置环境变量**
   编辑 `docker-compose.yml`，设置：
   ```yaml
   - RESEND_API_KEY=re_你的API密钥
   - SENDER_FROM_ADDRESS=名称 <alerts@已验证域名.com>
   - RECIPIENT_EMAIL=你的邮箱@example.com
   - SERVER_NAME=服务器名称
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **查看日志**
   ```bash
   docker-compose logs -f
   ```

## 网络检测
默认检测目标（可自定义）：
- 内网：192.168.1.1, 192.168.0.1
- 外网：114.114.114.114, 223.5.5.5, baidu.com
- DNS：baidu.com

使用环境变量 `INTERNAL_TARGETS`, `EXTERNAL_TARGETS`, `DNS_TARGET` 自定义检测目标。

## Dockerfile选项
- `Dockerfile` (默认): 使用国内镜像加速，构建更快
- `Dockerfile.original`: 不使用镜像，使用官方源

切换Dockerfile:
```bash
# 使用加速版本（默认）
docker-compose build

# 使用原始版本  
docker-compose -f docker-compose.yml build --build-arg DOCKERFILE=Dockerfile.original
```
