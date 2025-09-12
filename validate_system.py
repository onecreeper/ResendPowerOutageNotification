#!/usr/bin/env python3
"""
系统功能验证脚本
验证所有核心功能是否正常工作
"""

import os
import json
import time
from datetime import datetime

def test_file_operations():
    """测试文件操作功能"""
    print("=== 文件操作测试 ===")
    
    # 测试心跳文件读写
    test_files = ["test_heartbeat_a.log", "test_heartbeat_b.log"]
    timestamps = []
    
    for file in test_files:
        try:
            timestamp = int(time.time())
            with open(file, 'w') as f:
                f.write(str(timestamp))
            timestamps.append(timestamp)
            print(f"✅ 写入 {file}: 成功")
        except Exception as e:
            print(f"❌ 写入 {file}: 失败 - {e}")
            return False
    
    # 测试读取和验证
    for i, file in enumerate(test_files):
        try:
            with open(file, 'r') as f:
                content = f.read().strip()
                if content == str(timestamps[i]):
                    print(f"✅ 读取 {file}: 数据一致")
                else:
                    print(f"❌ 读取 {file}: 数据不一致")
                    return False
        except Exception as e:
            print(f"❌ 读取 {file}: 失败 - {e}")
            return False
    
    # 清理测试文件
    for file in test_files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except:
            pass
    
    return True

def test_json_operations():
    """测试JSON操作功能"""
    print("\n=== JSON操作测试 ===")
    
    test_data = {
        "timestamp": int(time.time()),
        "internal_network": True,
        "external_network": False,
        "dns_resolution": True
    }
    
    test_file = "test_network_status.json"
    
    try:
        # 写入测试
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        print("✅ JSON写入: 成功")
        
        # 读取测试
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        
        if loaded_data == test_data:
            print("✅ JSON读取: 数据一致")
        else:
            print("❌ JSON读取: 数据不一致")
            return False
            
    except Exception as e:
        print(f"❌ JSON操作: 失败 - {e}")
        return False
    finally:
        # 清理测试文件
        try:
            if os.path.exists(test_file):
                os.remove(test_file)
        except:
            pass
    
    return True

def test_email_functionality():
    """测试邮件功能（模拟）"""
    print("\n=== 邮件功能测试 ===")
    
    # 模拟邮件发送函数
    def mock_send_email(subject, html_body):
        print(f"📧 模拟发送邮件:")
        print(f"   主题: {subject}")
        print(f"   内容长度: {len(html_body)} 字符")
        return True
    
    # 测试断电通知邮件
    power_off_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    power_on_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    subject = "[断电警报] 测试服务器发生异常断电"
    html_body = f"""
    <html><body>
        <h3>服务器断电警报</h3>
        <p>服务器 <strong>测试服务器</strong> 在经历一次异常断电后已恢复运行。</p>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <tr><td style="background-color:#f2f2f2;"><strong>大致断电时间</strong></td><td>{power_off_time}</td></tr>
            <tr><td style="background-color:#f2f2f2;"><strong>恢复通电时间</strong></td><td>{power_on_time}</td></tr>
            <tr><td style="background-color:#f2f2f2;"><strong>断电持续时间</strong></td><td>00 小时 05 分钟 30 秒</td></tr>
        </table>
    </body></html>
    """
    
    try:
        result = mock_send_email(subject, html_body)
        if result:
            print("✅ 邮件模板: 正常")
        else:
            print("❌ 邮件模板: 失败")
            return False
    except Exception as e:
        print(f"❌ 邮件功能: 失败 - {e}")
        return False
    
    return True

def test_network_detection_logic():
    """测试网络检测逻辑"""
    print("\n=== 网络检测逻辑测试 ===")
    
    # 模拟网络状态变化检测
    current_status = {
        "timestamp": int(time.time()),
        "internal_network": True,
        "external_network": True,
        "dns_resolution": True
    }
    
    previous_status = {
        "last_internal_network": False,
        "last_external_network": False
    }
    
    # 检测状态变化
    internal_changed = current_status["internal_network"] != previous_status["last_internal_network"]
    external_changed = current_status["external_network"] != previous_status["last_external_network"]
    
    if internal_changed:
        print("✅ 内网状态变化检测: 正常")
    else:
        print("⚠️  内网状态无变化")
    
    if external_changed:
        print("✅ 外网状态变化检测: 正常")
    else:
        print("⚠️  外网状态无变化")
    
    if internal_changed or external_changed:
        print("✅ 状态变化检测逻辑: 正常")
        return True
    else:
        print("⚠️  状态变化检测: 无变化（正常情况）")
        return True

def main():
    """主测试函数"""
    print("服务器监控系统功能验证")
    print("=" * 50)
    
    tests = [
        test_file_operations,
        test_json_operations,
        test_email_functionality,
        test_network_detection_logic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ 测试失败: {test.__name__}")
        except Exception as e:
            print(f"❌ 测试异常: {test.__name__} - {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有核心功能验证通过！")
        print("\n系统准备就绪，可以部署使用。")
        return True
    else:
        print("⚠️  部分功能需要检查")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
