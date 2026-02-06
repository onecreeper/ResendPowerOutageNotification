# 场景测试指南

本文档说明如何使用 `test_scenarios.py` 测试电力监控系统的各种场景。

## 前置条件

### 1. 获取 Resend API Key

1. 访问 [Resend.com](https://resend.com)
2. 注册账号并登录
3. 进入 Dashboard → API Keys
4. 创建新的 API Key

### 2. 验证域名

1. 在 Resend Dashboard 中添加域名
2. 按照指引配置 DNS 记录
3. 等待域名验证通过

### 3. 配置环境变量

在 Windows 上设置环境变量：

```cmd
set RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxx
set SENDER_FROM_ADDRESS=服务器警卫 <alerts@your-verified-domain.com>
set RECIPIENT_EMAIL=your_personal_email@example.com
```

在 Linux/Mac 上：

```bash
export RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxx
export SENDER_FROM_ADDRESS="服务器警卫 <alerts@your-verified-domain.com>"
export RECIPIENT_EMAIL=your_personal_email@example.com
```

## 运行测试

### 启动测试工具

```cmd
python test_scenarios.py
```

### 可用测试场景

#### 1. 发送测试邮件

测试基本的邮件发送功能，验证：
- API Key 配置是否正确
- 发件人域名是否已验证
- 收件人是否能收到邮件

**预期结果**：收到测试邮件，邮件内容包含测试时间戳

#### 2. 模拟断电场景

模拟服务器断电后重启的场景：

- 创建5分钟前的心跳文件
- 运行 main.py 检测断电
- 生成待发送通知

**预期结果**：
- 检测到断电
- 生成断电通知到待发送队列
- 邮件内容包含断电时间和持续时长

#### 3. 模拟断网场景

模拟网络状态变化：

- 创建正常的心跳文件
- 设置网络状态为"内网正常，外网断开"
- 运行 main.py 检测网络变化

**预期结果**：
- 检测到外网中断
- 发送网络状态变化通知
- 邮件内容显示内网和外网状态变化

#### 4. 发送待处理通知

测试网络恢复后发送待处理通知：

- 创建待发送通知队列
- 模拟网络恢复（外网正常）
- 发送队列中的通知

**预期结果**：
- 成功发送待处理通知
- 收件箱收到断电/网络异常通知

#### 5. 运行所有测试

依次执行所有测试场景。

## 测试流程示例

### 完整测试流程

1. **配置环境变量**
   ```cmd
   set RESEND_API_KEY=re_your_api_key
   set SENDER_FROM_ADDRESS=监控 <alerts@your-domain.com>
   set RECIPIENT_EMAIL=your@email.com
   ```

2. **运行测试工具**
   ```cmd
   python test_scenarios.py
   ```

3. **选择测试场景**
   - 输入 `1` 测试邮件发送
   - 输入 `5` 运行所有测试

4. **检查邮件**
   - 登录收件人邮箱
   - 查看是否收到测试邮件
   - 验证邮件内容是否正确

## 预期邮件内容

### 测试邮件示例

```
主题: [测试] 电力监控系统测试邮件 - 2026-02-06 14:30:00

内容:
📧 测试邮件

如果你收到这封邮件，说明邮件发送功能正常！

─────────────────────────────────────
测试时间: 2026-02-06 14:30:00
测试场景: 基本邮件发送测试
```

### 断电警报邮件示例

```
主题: [断电警报] 服务器 测试服务器 发生异常断电

内容:
服务器断电警报

服务器 测试服务器 在经历一次异常断电后已恢复运行。

┌─────────────────────────────────────┐
│ 大致断电时间    │ 2026-02-06 14:20:00 │
│ 恢复通电时间    │ 2026-02-06 14:25:00 │
│ 断电持续时间    │ 00 小时 05 分钟 00 秒 │
└─────────────────────────────────────┘
```

### 网络状态变化邮件示例

```
主题: [网络状态] 服务器 测试服务器 网络连接变化

内容:
服务器网络状态变化通知

服务器 测试服务器 的网络连接状态发生变化：

┌─────────────────────────────────────────────────────────────┐
│ 网络类型      │ 之前状态 │ 当前状态 │ 变化时间              │
├─────────────────────────────────────────────────────────────┤
│ 内网连接      │ 正常     │ 正常     │ 2026-02-06 14:30:00  │
│ 外网连接      │ 正常     │ 中断     │ 2026-02-06 14:30:00  │
└─────────────────────────────────────────────────────────────┘

DNS解析: 异常
```

## 故障排查

### 问题 1: 邮件发送失败

**错误信息**: `使用 Resend 发送邮件失败`

**可能原因**:
- API Key 无效或已过期
- 发件人域名未验证
- 收件人邮箱地址无效

**解决方法**:
1. 检查 RESEND_API_KEY 是否正确
2. 在 Resend Dashboard 确认域名已验证
3. 检查收件人邮箱地址格式

### 问题 2: 未收到邮件

**可能原因**:
- 邮件被标记为垃圾邮件
- 邮箱地址错误
- 发送延迟

**解决方法**:
1. 检查垃圾邮件文件夹
2. 验证收件人邮箱地址
3. 等待几分钟后再检查

### 问题 3: 测试脚本无法运行

**错误信息**: `ModuleNotFoundError: No module named 'resend'`

**解决方法**:
```cmd
pip install resend
```

## 注意事项

1. **API Key 安全**: 不要将 API Key 提交到版本控制系统
2. **域名验证**: 确保在 Resend 上验证了发件人域名
3. **邮件频率**: 避免短时间内发送过多测试邮件
4. **测试环境**: 建议先使用测试环境，确认无误后再部署到生产环境

## Docker 部署测试

如果要在 Docker 中测试，修改 `docker-compose.yml`：

```yaml
environment:
  - RESEND_API_KEY=re_your_api_key
  - SENDER_FROM_ADDRESS=服务器警卫 <alerts@your-verified-domain.com>
  - RECIPIENT_EMAIL=your@email.com
  - SERVER_NAME=测试服务器
```

然后运行：

```cmd
docker-compose up -d
docker-compose logs -f
```

## 下一步

测试通过后，可以：

1. 部署到生产服务器
2. 配置实际的监控目标
3. 设置合适的阈值参数
4. 定期检查系统日志

## 联系支持

如有问题，请查看：
- [Resend 官方文档](https://resend.com/docs)
- [项目 README](README.md)
- [单元测试文档](pytest.ini)