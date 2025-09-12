import time
import os
import json
import subprocess
import socket

HEARTBEAT_FILE_A = "/data/heartbeat_a.log"
HEARTBEAT_FILE_B = "/data/heartbeat_b.log"
NETWORK_STATUS_FILE = "/data/network_status.log"
HEARTBEAT_INTERVAL = 60  # 秒

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
        with open(NETWORK_STATUS_FILE, 'w') as f:
            json.dump(status, f)
    except Exception as e:
        print(f"保存网络状态错误: {e}")

print("--- 后台任务：心跳服务已启动（增强版）---")
use_file_a = True

while True:
    target_file = HEARTBEAT_FILE_A if use_file_a else HEARTBEAT_FILE_B
    
    try:
        # 更新心跳文件
        os.makedirs("/data", exist_ok=True)
        with open(target_file, 'w') as f:
            f.write(str(int(time.time())))
        
        # 检查并保存网络状态
        network_status = check_network_connectivity()
        save_network_status(network_status)
        
        print(f"心跳更新: {time.strftime('%Y-%m-%d %H:%M:%S')} - "
              f"内网: {'正常' if network_status['internal_network'] else '异常'} - "
              f"外网: {'正常' if network_status['external_network'] else '异常'}")
              
    except Exception as e:
        print(f"心跳错误：更新失败: {e}")
    
    use_file_a = not use_file_a
    time.sleep(HEARTBEAT_INTERVAL)
