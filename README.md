# 服务器监控系统

断电和网络状态监控，状态变化时自动发送邮件通知。

## 功能
- 断电检测和恢复通知
- 内网和外网连接监控
- 网络状态变化实时通知
- 自愈功能和稳定性保障
- 邮件发送失败自动重试

## 快速开始

### 1. 准备工作

#### 获取 Resend API Key
1. 访问 [Resend.com](https://resend.com) 注册账号
2. 进入 Dashboard → API Keys 创建新的 API Key
3. 在 Dashboard → Domains 添加并验证你的域名

#### 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
# Windows: notepad .env
# Linux/Mac: nano .env
```

编辑 `.env` 文件，填写以下必需配置：

```env
# 必需配置
RESEND_API_KEY=re_your_api_key_here
SENDER_FROM_ADDRESS=服务器警卫 <alerts@your-verified-domain.com>
RECIPIENT_EMAIL=your_email@example.com

# 可选配置
SERVER_NAME=跳板机
OUTAGE_THRESHOLD=180
NETWORK_OUTAGE_THRESHOLD=300
INTERNAL_TARGETS=192.168.1.1,192.168.0.1
EXTERNAL_TARGETS=114.114.114.114,223.5.5.5,baidu.com
DNS_TARGET=baidu.com
TZ=Asia/Shanghai
```

### 2. 启动服务

```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 验证服务

```bash
# 检查容器是否正常运行
docker ps | grep power-monitor

# 查看最近日志
docker-compose logs --tail=50
```

## 配置说明

### 必需配置

| 变量 | 说明 | 示例 |
|------|------|------|
| `RESEND_API_KEY` | Resend API 密钥 | `re_xxxxxxxxxxxx` |
| `SENDER_FROM_ADDRESS` | 发件人地址 | `服务器警卫 <alerts@your-domain.com>` |
| `RECIPIENT_EMAIL` | 收件人邮箱 | `your@email.com` |

### 可选配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SERVER_NAME` | 服务器名称 | `跳板机` |
| `OUTAGE_THRESHOLD` | 断电判定阈值（秒） | `180` (3分钟) |
| `NETWORK_OUTAGE_THRESHOLD` | 网络异常阈值（秒） | `300` (5分钟) |
| `INTERNAL_TARGETS` | 内网检测目标 | `192.168.1.1,192.168.0.1` |
| `EXTERNAL_TARGETS` | 外网检测目标 | `114.114.114.114,223.5.5.5,baidu.com` |
| `DNS_TARGET` | DNS 检测目标 | `baidu.com` |
| `TZ` | 时区 | `Asia/Shanghai` |

## 网络检测

默认检测目标：
- **内网**: 192.168.1.1, 192.168.0.1
- **外网**: 114.114.114.114, 223.5.5.5, baidu.com
- **DNS**: baidu.com

可在 `.env` 文件中通过 `INTERNAL_TARGETS`、`EXTERNAL_TARGETS`、`DNS_TARGET` 自定义。

## Dockerfile 选项

- `Dockerfile` (默认): 使用国内镜像加速，构建更快
- `Dockerfile.original`: 不使用镜像，使用官方源

切换 Dockerfile:

```bash
# 使用加速版本（默认）
docker-compose build

# 使用原始版本
docker-compose -f docker-compose.yml build --build-arg DOCKERFILE=Dockerfile.original
```

## 测试

### 本地测试

运行场景测试：

```bash
# 交互式测试
python test_scenarios.py

# 快速自动化测试
python quick_test.py

# Windows 用户
run_test.bat
```

详细测试说明请查看 [TEST_GUIDE.md](TEST_GUIDE.md)

### 单元测试

```bash
# 安装测试依赖
pip install -r requirements-dev.txt

# 运行所有测试
pytest -v

# 运行特定测试
pytest tests/test_main.py -v
pytest tests/test_heartbeat.py -v
```

## 常见操作

### 查看日志

```bash
# 实时查看日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100

# 查看特定时间段的日志
docker-compose logs --since 2026-02-06T10:00:00
```

### 重启服务

```bash
# 重启服务
docker-compose restart

# 停止服务
docker-compose stop

# 启动服务
docker-compose start
```

### 更新服务

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build

# 清理旧镜像（可选）
docker image prune -f
```

### 查看数据

```bash
# 进入容器
docker exec -it power-monitor-pro /bin/bash

# 查看心跳文件
cat /data/heartbeat_a.log
cat /data/heartbeat_b.log

# 查看网络状态
cat /data/network_status.log

# 查看待发送通知
cat /data/pending_notifications.log
```

## 故障排查

### 问题 1: 邮件未收到

检查步骤：

```bash
# 1. 查看服务日志
docker-compose logs -f | grep "邮件"

# 2. 检查环境变量
docker-compose config

# 3. 进入容器检查配置
docker exec -it power-monitor-pro env | grep RESEND
```

### 问题 2: 服务无法启动

```bash
# 查看详细日志
docker-compose logs --tail=100

# 检查容器状态
docker-compose ps

# 重新构建
docker-compose up -d --force-recreate
```

### 问题 3: 数据丢失

确保 volumes 正确挂载：

```bash
# 检查 volumes
docker volume ls

# 备份数据
docker cp power-monitor-pro:/data ./backup_data
```

## 项目结构

```
.
├── app/
│   ├── main.py           # 主程序：断电检测
│   ├── heartbeat.py      # 心跳服务：网络监控
│   └── entrypoint.sh     # 容器入口
├── tests/                # 单元测试
│   ├── test_main.py
│   ├── test_heartbeat.py
│   └── conftest.py
├── power_monitor_data/   # 数据持久化目录
├── docker-compose.yml    # Docker 编排文件
├── Dockerfile            # 镜像构建文件
├── .env.example          # 环境变量模板
├── .env                  # 环境变量文件（需创建）
├── test_scenarios.py     # 场景测试工具
├── quick_test.py         # 快速测试脚本
├── run_test.bat          # Windows 测试脚本
└── TEST_GUIDE.md         # 测试指南
```

## 安全建议

1. **保护 API Key**: 不要将 `.env` 文件提交到版本控制
2. **使用强密码**: 为服务器和邮箱使用强密码
3. **定期更新**: 保持系统和依赖包的最新版本
4. **监控日志**: 定期检查系统日志，及时发现异常

## 相关文档

- [测试指南](TEST_GUIDE.md) - 详细的场景测试说明
- [环境变量模板](.env.example) - 所有可配置的变量

## 许可证

MIT License
