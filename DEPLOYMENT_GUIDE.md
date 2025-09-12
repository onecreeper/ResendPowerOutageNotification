# 服务器监控系统部署指南

## 系统概述

这是一个功能完整的服务器断电和网络监控系统，具有以下核心功能：

- ✅ **断电检测**: 检测服务器异常断电并发送恢复通知
- ✅ **内网监控**: 实时监控内网连接状态（路由器可达性）
- ✅ **外网监控**: 实时监控外网连接状态（互联网可达性）  
- ✅ **DNS检测**: 监控DNS解析功能
- ✅ **状态变化通知**: 网络状态变化时立即发送邮件通知
- ✅ **自愈功能**: 自动修复损坏的心跳文件
- ✅ **严格稳定性**: 多重保障确保系统可靠运行

## 快速开始

### 1. 环境要求

- Docker 和 Docker Compose
- Resend.com 账户和API密钥
- 已验证的域名邮箱（用于发件）

### 2. 配置步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/onecreeper/ResendPowerOutageNotification.git
   cd ResendPowerOutageNotification
   ```

2. **配置环境变量**
   
   编辑 `docker-compose.yml` 文件，修改以下配置：
   
   ```yaml
   environment:
     # Resend.com配置
     - RESEND_API_KEY=re_你的实际API密钥
     - SENDER_FROM_ADDRESS=服务器监控 <alerts@your-verified-domain.com>
     - RECIPIENT_EMAIL=your_email@example.com
     
     # 服务器配置
     - SERVER_NAME=你的服务器名称
     - OUTAGE_THRESHOLD=180      # 断电判定阈值（秒）
     - NETWORK_OUTAGE_THRESHOLD=300  # 网络异常阈值（秒）
     
     # 网络检测配置（可选，使用中国大陆友好的默认值）
     - INTERNAL_TARGETS=192.168.1.1,192.168.0.1    # 内网检测目标
     - EXTERNAL_TARGETS=114.114.114.114,223.5.5.5,baidu.com  # 外网检测目标
     - DNS_TARGET=baidu.com      # DNS检测目标
     
     - TZ=Asia/Shanghai          # 时区设置
   ```

3. **启动服务**
   
   **Windows用户**:
   ```cmd
   start.bat
   ```
   
   **Linux/Mac用户**:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   
   或手动启动:
   ```bash
   docker-compose up -d
   ```

### 3. 验证部署

查看服务日志确认运行状态：
```bash
docker-compose logs -f
```

正常输出应包含：
```
--- 启动检查：断电监控服务（自愈模式） ---
--- 后台任务：心跳服务已启动（增强版）---
心跳更新: 2025-09-12 22:30:45 - 内网: 正常 - 外网: 正常
```

## 功能详解

### 断电检测机制

系统使用双心跳文件机制：
- `heartbeat_a.log` 和 `heartbeat_b.log` 交替更新
- 每60秒更新一次时间戳
- 重启时检查时间差，超过阈值判定为异常断电

### 网络检测机制

**内网检测**:
- 默认检测常见路由器IP: `192.168.1.1`, `192.168.0.1`
- 可通过 `INTERNAL_TARGETS` 环境变量自定义
- 使用ping命令验证可达性

**外网检测**:
- 默认检测国内DNS: `114.114.114.114`, `223.5.5.5`
- 默认检测网站: `baidu.com`（中国大陆友好）
- 可通过 `EXTERNAL_TARGETS` 环境变量自定义
- 验证DNS解析功能（使用 `DNS_TARGET` 配置）

### 邮件通知类型

1. **断电恢复通知**
   - 当服务器异常断电后恢复时发送
   - 包含断电时间、恢复时间、持续时间

2. **网络状态变化通知**
   - 当内网或外网连接状态变化时发送
   - 显示之前状态、当前状态、变化时间

## 高级配置

### 自定义网络检测目标

通过环境变量配置，无需修改代码：

```yaml
# 自定义内网检测目标
- INTERNAL_TARGETS=192.168.31.1,192.168.1.254,你的路由器IP

# 自定义外网检测目标  
- EXTERNAL_TARGETS=8.8.8.8,1.1.1.1,google.com,你的常用网站

# 自定义DNS检测目标
- DNS_TARGET=google.com
```

### 调整检测频率

修改 `HEARTBEAT_INTERVAL`（秒）：
```python
HEARTBEAT_INTERVAL = 30  # 更频繁的检测
```

### 数据持久化

监控数据保存在 `./power_monitor_data/` 目录：
- 心跳文件时间戳
- 网络状态记录
- 网络历史状态

## 故障排除

### 常见问题

1. **邮件发送失败**
   - 检查 Resend API 密钥是否正确
   - 确认发件邮箱域名已验证
   - 检查收件邮箱地址是否正确

2. **网络检测异常**
   - 检查防火墙是否允许ping命令
   - 确认网络检测目标可达

3. **容器启动失败**
   - 检查 Docker 和 Docker Compose 版本
   - 查看详细日志: `docker-compose logs`

### 日志分析

查看详细日志：
```bash
docker-compose logs power-monitor
```

关键日志信息：
- `心跳更新`: 正常的心跳更新
- `检测到异常断电`: 断电事件
- `网络状态变化`: 网络连接状态变化
- `使用 Resend 发送邮件失败`: 邮件发送问题

## 系统维护

### 更新系统

```bash
git pull origin main
docker-compose build
docker-compose up -d
```

### 数据备份

重要数据目录：
- `./power_monitor_data/`: 监控数据文件

### 监控系统本身

建议使用外部监控工具监控本系统的Docker容器状态。

## 安全考虑

1. **API密钥保护**
   - 不要将包含真实API密钥的配置文件提交到版本控制
   - 考虑使用环境变量或密钥管理服务

2. **网络权限**
   - 容器需要网络访问权限进行检测
   - 确保适当的防火墙规则

3. **数据安全**
   - 监控数据包含服务器时间信息
   - 定期清理旧数据（如果需要）

## 技术支持

如果遇到问题：
1. 查看详细日志
2. 检查配置是否正确
3. 参考本项目GitHub Issues

---

**注意**: 在生产环境部署前，请务必在测试环境充分验证所有功能。
