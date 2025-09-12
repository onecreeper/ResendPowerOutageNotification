import os
import resend
import time
import json
from datetime import datetime

# --- 配置：从环境变量读取 ---
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_FROM_ADDRESS = os.getenv("SENDER_FROM_ADDRESS")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

HEARTBEAT_FILE_A = "/data/heartbeat_a.log"
HEARTBEAT_FILE_B = "/data/heartbeat_b.log"
NETWORK_STATUS_FILE = "/data/network_status.log"
NETWORK_HISTORY_FILE = "/data/network_history.log"
OUTAGE_THRESHOLD = int(os.getenv("OUTAGE_THRESHOLD", 180))
NETWORK_OUTAGE_THRESHOLD = int(os.getenv("NETWORK_OUTAGE_THRESHOLD", 300))  # 5分钟
SERVER_NAME = os.getenv("SERVER_NAME", "Unknown Server")

def send_email_with_resend(subject, html_body):
    """使用 Resend API 发送邮件"""
    if not all([RESEND_API_KEY, SENDER_FROM_ADDRESS, RECIPIENT_EMAIL]):
        print("错误：邮件配置环境变量不完整。无法发送邮件。")
        return

    resend.api_key = RESEND_API_KEY
    params = {
        "from": SENDER_FROM_ADDRESS,
        "to": [RECIPIENT_EMAIL],
        "subject": subject,
        "html": html_body,
    }
    try:
        email = resend.Emails.send(params)
        print(f"邮件已通过 Resend 发送成功！ Email ID: {email['id']}")
    except Exception as e:
        print(f"使用 Resend 发送邮件失败: {e}")

def _get_valid_timestamp(filepath):
    """安全地从文件中读取时间戳，返回(时间戳, 状态)"""
    if not os.path.isfile(filepath):
        return None, "non-existent"
    try:
        with open(filepath, 'r') as f:
            content = f.read().strip()
            if not content:
                return None, "empty"
            return int(content), "valid"
    except (ValueError, IOError):
        return None, "corrupted"

def _write_timestamp(filepath, ts):
    """将时间戳写入文件，用于修复"""
    try:
        with open(filepath, 'w') as f:
            f.write(str(ts))
        print(f"修复日志：已将时间戳 {ts} 写入文件 {filepath}。")
    except IOError as e:
        print(f"错误：写入文件 {filepath} 失败: {e}")

def _remove_file(filepath):
    """安全地删除文件，用于清理"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"修复日志：已删除无效文件 {filepath}。")
    except OSError as e:
        print(f"错误：删除文件 {filepath} 失败: {e}")

def _load_network_status():
    """加载网络状态文件"""
    if not os.path.isfile(NETWORK_STATUS_FILE):
        return None
    
    try:
        with open(NETWORK_STATUS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def _load_network_history():
    """加载网络历史记录"""
    if not os.path.isfile(NETWORK_HISTORY_FILE):
        return {"last_internal_network": True, "last_external_network": True}
    
    try:
        with open(NETWORK_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"last_internal_network": True, "last_external_network": True}

def _save_network_history(history):
    """保存网络历史记录"""
    try:
        with open(NETWORK_HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except IOError as e:
        print(f"保存网络历史记录失败: {e}")

def check_network_status_changes():
    """检查网络状态变化并发送通知"""
    current_status = _load_network_status()
    if not current_status:
        print("无法读取当前网络状态，跳过网络检查")
        return
    
    history = _load_network_history()
    
    current_time = int(time.time())
    status_age = current_time - current_status["timestamp"]
    
    # 如果状态数据太旧（超过5分钟），认为网络检测可能有问题
    if status_age > 300:
        print(f"警告：网络状态数据已过期 ({status_age} 秒)，可能网络检测服务异常")
        return
    
    # 检查内网状态变化
    internal_changed = (current_status["internal_network"] != history["last_internal_network"])
    external_changed = (current_status["external_network"] != history["last_external_network"])
    
    if internal_changed or external_changed:
        # 发送网络状态变化通知
        send_network_status_email(current_status, history)
        
        # 更新历史记录
        history["last_internal_network"] = current_status["internal_network"]
        history["last_external_network"] = current_status["external_network"]
        _save_network_history(history)
        
        print("网络状态变化已检测并通知")
    else:
        print("网络状态无变化")

def send_network_status_email(current_status, previous_status):
    """发送网络状态变化邮件"""
    internal_status = "恢复正常" if current_status["internal_network"] else "中断"
    external_status = "恢复正常" if current_status["external_network"] else "中断"
    
    subject = f"[网络状态] 服务器 {SERVER_NAME} 网络连接变化"
    
    html_body = f"""
    <html><body>
        <h3>服务器网络状态变化通知</h3>
        <p>服务器 <strong>{SERVER_NAME}</strong> 的网络连接状态发生变化：</p>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <tr>
                <td style="background-color:#f2f2f2;"><strong>网络类型</strong></td>
                <td style="background-color:#f2f2f2;"><strong>之前状态</strong></td>
                <td style="background-color:#f2f2f2;"><strong>当前状态</strong></td>
                <td style="background-color:#f2f2f2;"><strong>变化时间</strong></td>
            </tr>
            <tr>
                <td><strong>内网连接</strong></td>
                <td>{'正常' if previous_status['last_internal_network'] else '中断'}</td>
                <td>{'正常' if current_status['internal_network'] else '中断'}</td>
                <td>{datetime.fromtimestamp(current_status['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</td>
            </tr>
            <tr>
                <td><strong>外网连接</strong></td>
                <td>{'正常' if previous_status['last_external_network'] else '中断'}</td>
                <td>{'正常' if current_status['external_network'] else '中断'}</td>
                <td>{datetime.fromtimestamp(current_status['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</td>
            </tr>
        </table>
        <p>DNS解析: {'正常' if current_status['dns_resolution'] else '异常'}</p>
    </body></html>
    """
    
    print(f"发送网络状态变化邮件: 内网{internal_status}, 外网{external_status}")
    send_email_with_resend(subject, html_body)

def main():
    print("--- 启动检查：断电监控服务（自愈模式） ---")
    os.makedirs("/data", exist_ok=True)

    # 读取两个心跳文件的状态
    ts_a, status_a = _get_valid_timestamp(HEARTBEAT_FILE_A)
    ts_b, status_b = _get_valid_timestamp(HEARTBEAT_FILE_B)

    # 自动修复逻辑
    if status_a != "valid" and status_b == "valid":
        print(f"状态：检测到文件A损坏（{status_a}），文件B正常。")
        _write_timestamp(HEARTBEAT_FILE_A, ts_b)
        ts_a = ts_b
    elif status_b != "valid" and status_a == "valid":
        print(f"状态：检测到文件B损坏（{status_b}），文件A正常。")
        _write_timestamp(HEARTBEAT_FILE_B, ts_a)
        ts_b = ts_a
    elif status_a != "valid" and status_b != "valid":
        print("警告：两个心跳文件均无效！")
        _remove_file(HEARTBEAT_FILE_A)
        _remove_file(HEARTBEAT_FILE_B)
        print("状态：已清理现场。可能是首次运行，本次跳过检查。")
        return

    # 确定最新的有效时间戳
    last_alive_ts = max(ts_a, ts_b)
    power_on_ts = int(time.time())
    duration_seconds = power_on_ts - last_alive_ts

    print(f"最后心跳: {datetime.fromtimestamp(last_alive_ts)}")
    print(f"当前启动: {datetime.fromtimestamp(power_on_ts)}")
    print(f"时间差: {duration_seconds} 秒")

    # 判断是否为异常断电并发送邮件
    if duration_seconds > OUTAGE_THRESHOLD:
        power_off_time = datetime.fromtimestamp(last_alive_ts).strftime('%Y-%m-%d %H:%M:%S')
        power_on_time = datetime.fromtimestamp(power_on_ts).strftime('%Y-%m-%d %H:%M:%S')
        h, rem = divmod(duration_seconds, 3600)
        m, s = divmod(rem, 60)
        duration_formatted = f"{h:02d} 小时 {m:02d} 分钟 {s:02d} 秒"

        subject = f"[断电警报] 服务器 {SERVER_NAME} 发生异常断电"
        html_body = f"""
        <html><body>
            <h3>服务器断电警报</h3>
            <p>服务器 <strong>{SERVER_NAME}</strong> 在经历一次异常断电后已恢复运行。</p>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
                <tr><td style="background-color:#f2f2f2;"><strong>大致断电时间</strong></td><td>{power_off_time}</td></tr>
                <tr><td style="background-color:#f2f2f2;"><strong>恢复通电时间</strong></td><td>{power_on_time}</td></tr>
                <tr><td style="background-color:#f2f2f2;"><strong>断电持续时间</strong></td><td>{duration_formatted}</td></tr>
            </table>
        </body></html>
        """
        print("检测到异常断电，准备通过 Resend 发送邮件...")
        send_email_with_resend(subject, html_body)
    else:
        print("状态：时间差在阈值内，判定为正常重启或服务重启。")
    
    # 检查网络状态变化
    print("\n--- 检查网络状态变化 ---")
    check_network_status_changes()

if __name__ == "__main__":
    main()
