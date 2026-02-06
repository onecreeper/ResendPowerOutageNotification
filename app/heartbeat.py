import time
import os
import json
import subprocess
import socket
from app.file_lock import file_lock
from app.retry_utils import retry_with_backoff, is_retryable_error

HEARTBEAT_FILE_A = "/data/heartbeat_a.log"
HEARTBEAT_FILE_B = "/data/heartbeat_b.log"
NETWORK_STATUS_FILE = "/data/network_status.log"
PENDING_NOTIFICATIONS_FILE = "/data/pending_notifications.log"
HEARTBEAT_INTERVAL = 60  # 秒

# 从环境变量获取邮件配置
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_FROM_ADDRESS = os.getenv("SENDER_FROM_ADDRESS")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
SERVER_NAME = os.getenv("SERVER_NAME", "Unknown Server")

# 从环境变量获取网络检测配置
def get_network_targets():
    """从环境变量获取网络检测目标"""
    # 内网检测目标（默认值）
    internal_default = ["192.168.1.1", "192.168.0.1"]
    internal_env = os.getenv("INTERNAL_TARGETS", "")
    internal_hosts = internal_env.split(",") if internal_env else internal_default
    internal_hosts = [host.strip() for host in internal_hosts if host.strip()]
    
    # 外网检测目标（默认使用中国大陆友好的地址）
    external_default = ["114.114.114.114", "223.5.5.5", "baidu.com"]
    external_env = os.getenv("EXTERNAL_TARGETS", "")
    external_hosts = external_env.split(",") if external_env else external_default
    external_hosts = [host.strip() for host in external_hosts if host.strip()]
    
    # DNS检测目标
    dns_default = "baidu.com"
    dns_target = os.getenv("DNS_TARGET", dns_default)
    
    return {
        "internal": internal_hosts,
        "external": external_hosts,
        "dns": dns_target
    }

def check_network_connectivity():
    """检查网络连接状态"""
    status = {
        "timestamp": int(time.time()),
        "internal_network": False,
        "external_network": False,
        "dns_resolution": False
    }
    
    # 获取网络检测目标配置
    targets = get_network_targets()
    
    # 检查DNS解析
    try:
        socket.gethostbyname(targets["dns"])
        status["dns_resolution"] = True
    except socket.gaierror:
        status["dns_resolution"] = False
    
    # 检测操作系统类型，使用相应的ping参数
    import platform
    if platform.system().lower() == "windows":
        ping_args = ["ping", "-n", "1", "-w", "2000"]
    else:
        ping_args = ["ping", "-c", "1", "-W", "2"]
    
    # 检查内网连接
    for host in targets["internal"]:
        try:
            cmd = ping_args + [host]
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            if result.returncode == 0:
                status["internal_network"] = True
                break
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            continue
    
    # 检查外网连接
    for host in targets["external"]:
        try:
            cmd = ping_args + [host]
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            if result.returncode == 0:
                status["external_network"] = True
                break
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            continue
    
    return status

def save_network_status(status):
    """保存网络状态到文件"""
    try:
        os.makedirs("/data", exist_ok=True)
        with file_lock(NETWORK_STATUS_FILE):
            with open(NETWORK_STATUS_FILE, 'w') as f:
                json.dump(status, f)
    except Exception as e:
        print(f"保存网络状态错误: {e}")

def _load_pending_notifications():
    """加载待发送通知队列"""
    if not os.path.isfile(PENDING_NOTIFICATIONS_FILE):
        return []
    
    try:
        with file_lock(PENDING_NOTIFICATIONS_FILE):
            with open(PENDING_NOTIFICATIONS_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def _save_pending_notifications(notifications):
    """保存待发送通知队列"""
    try:
        with file_lock(PENDING_NOTIFICATIONS_FILE):
            with open(PENDING_NOTIFICATIONS_FILE, 'w') as f:
                json.dump(notifications, f)
    except IOError as e:
        print(f"保存待发送通知失败: {e}")

def send_email_with_resend(subject, html_body):
    """使用 Resend API 发送邮件（带重试机制）"""
    if not all([RESEND_API_KEY, SENDER_FROM_ADDRESS, RECIPIENT_EMAIL]):
        print("错误：邮件配置环境变量不完整。无法发送邮件。")
        return False

    def send_email():
        """实际的发送邮件函数"""
        import resend
        resend.api_key = RESEND_API_KEY
        params = {
            "from": SENDER_FROM_ADDRESS,
            "to": [RECIPIENT_EMAIL],
            "subject": subject,
            "html": html_body,
        }
        email = resend.Emails.send(params)
        print(f"邮件已通过 Resend 发送成功！ Email ID: {email['id']}")
        return True
    
    try:
        # 使用重试机制：最多3次，初始延迟1秒，指数退避
        retry_with_backoff(
            send_email,
            max_retries=3,
            initial_delay=1,
            backoff_factor=2,
            exceptions=(Exception,),
            should_retry_func=is_retryable_error
        )
        return True
    except Exception as e:
        print(f"使用 Resend 发送邮件失败（所有重试均失败）: {e}")
        return False

def process_pending_notifications():
    """处理待发送的通知队列"""
    # 在同一个锁内完成读取操作
    with file_lock(PENDING_NOTIFICATIONS_FILE):
        try:
            if not os.path.isfile(PENDING_NOTIFICATIONS_FILE):
                return  # 文件不存在，无需处理
            
            with open(PENDING_NOTIFICATIONS_FILE, 'r') as f:
                notifications = json.load(f)
            
            if not notifications:
                return  # 队列为空，无需处理
        except (json.JSONDecodeError, IOError):
            return  # 读取失败，跳过处理
    
    # 在锁外发送邮件，避免长时间持有锁
    print(f"发现 {len(notifications)} 个待发送通知，尝试发送...")
    
    successful_notifications = []
    failed_notifications = []
    
    for notification in notifications:
        if send_email_with_resend(notification["subject"], notification["html_body"]):
            successful_notifications.append(notification)
        else:
            failed_notifications.append(notification)
    
    # 保存发送失败的通知（用于重试）
    _save_pending_notifications(failed_notifications)
    
    if successful_notifications:
        print(f"成功发送 {len(successful_notifications)} 个通知")
    if failed_notifications:
        print(f"仍有 {len(failed_notifications)} 个通知发送失败，将在下次重试")

def check_and_send_pending_notifications(network_status):
    """检查网络状态并发送待处理通知"""
    # 只有在外网正常时才尝试发送通知
    if network_status["external_network"]:
        process_pending_notifications()

if __name__ == "__main__":
    print("--- 后台任务：心跳服务已启动（增强版）---")
    
    # 确保数据目录存在并设置正确的权限
    os.makedirs("/data", exist_ok=True)
    try:
        os.chmod("/data", 0o700)  # 仅所有者可读写执行
    except Exception as e:
        print(f"警告：无法设置目录权限: {e}")
    
    use_file_a = True

    while True:
        target_file = HEARTBEAT_FILE_A if use_file_a else HEARTBEAT_FILE_B

        try:
            # 更新心跳文件
            os.makedirs("/data", exist_ok=True)
            with file_lock(target_file):
                with open(target_file, 'w') as f:
                    f.write(str(int(time.time())))

            # 检查并保存网络状态
            network_status = check_network_connectivity()
            save_network_status(network_status)

            print(f"心跳更新: {time.strftime('%Y-%m-%d %H:%M:%S')} - "
                  f"内网: {'正常' if network_status['internal_network'] else '异常'} - "
                  f"外网: {'正常' if network_status['external_network'] else '异常'}")

            # 检查并发送待处理通知
            check_and_send_pending_notifications(network_status)

        except Exception as e:
            print(f"心跳错误：更新失败: {e}")

        use_file_a = not use_file_a
        time.sleep(HEARTBEAT_INTERVAL)
