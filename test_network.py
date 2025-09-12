#!/usr/bin/env python3
"""
网络检测功能测试脚本
用于验证网络检测功能是否正常工作
"""

import subprocess
import socket
import time
import json

def test_network_connectivity():
    """测试网络连接功能"""
    print("=== 网络连接测试 ===")
    
    # 测试DNS解析
    try:
        socket.gethostbyname("google.com")
        print("✅ DNS解析: 正常")
    except socket.gaierror:
        print("❌ DNS解析: 失败")
    
    # Windows ping命令参数
    ping_cmd = ["ping", "-n", "1", "-w", "2000"]
    
    # 测试内网连接
    internal_hosts = ["192.168.1.1", "192.168.0.1"]
    internal_success = False
    for host in internal_hosts:
        try:
            cmd = ping_cmd + [host]
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✅ 内网连接 ({host}): 正常")
                internal_success = True
                break
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            continue
    
    if not internal_success:
        print("❌ 内网连接: 所有测试地址均失败")
    
    # 测试外网连接
    external_hosts = ["8.8.8.8", "1.1.1.1", "google.com"]
    external_success = False
    for host in external_hosts:
        try:
            cmd = ping_cmd + [host]
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✅ 外网连接 ({host}): 正常")
                external_success = True
                break
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            continue
    
    if not external_success:
        print("❌ 外网连接: 所有测试地址均失败")
        
def test_windows_network():
    """Windows特定的网络测试"""
    print("\n=== Windows网络测试 ===")
    
    # 测试基本的网络连通性
    try:
        # 测试是否能访问外部网站
        import urllib.request
        urllib.request.urlopen("http://www.google.com", timeout=5)
        print("✅ HTTP连接: 正常")
    except Exception:
        print("❌ HTTP连接: 失败")
        
    # 测试本地网络
    try:
        # 获取本机IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"✅ 本地网络: 正常 (IP: {local_ip})")
    except Exception:
        print("❌ 本地网络: 异常")

def test_heartbeat_function():
    """测试心跳功能"""
    print("\n=== 心跳功能测试 ===")
    
    try:
        # 模拟心跳文件写入（使用当前目录）
        test_timestamp = int(time.time())
        test_file = "test_heartbeat.log"
        
        with open(test_file, 'w') as f:
            f.write(str(test_timestamp))
        
        # 读取验证
        with open(test_file, 'r') as f:
            content = f.read().strip()
            if content == str(test_timestamp):
                print("✅ 心跳文件读写: 正常")
            else:
                print("❌ 心跳文件读写: 数据不一致")
        
        # 清理测试文件
        import os
        if os.path.exists(test_file):
            os.remove(test_file)
                
    except Exception as e:
        print(f"❌ 心跳功能测试失败: {e}")

if __name__ == "__main__":
    print("服务器监控系统功能测试")
    print("=" * 40)
    
    test_network_connectivity()
    test_windows_network()
    test_heartbeat_function()
    
    print("\n测试完成！")
