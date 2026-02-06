#!/usr/bin/env python
"""
测试脚本：模拟断电和断网场景

使用方法：
1. 设置正确的环境变量（RESEND_API_KEY, SENDER_FROM_ADDRESS, RECIPIENT_EMAIL）
2. 运行此脚本测试各种场景
"""

import os
import sys
import time
import json
import tempfile
import shutil
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_environment():
    """设置测试环境变量"""
    print("=" * 60)
    print("请确保已设置以下环境变量：")
    print("-" * 60)
    print("RESEND_API_KEY: 你的 Resend API Key")
    print("SENDER_FROM_ADDRESS: 发件人地址（已验证域名）")
    print("RECIPIENT_EMAIL: 收件人邮箱")
    print("=" * 60)
    print()

    # 检查环境变量
    required_vars = ['RESEND_API_KEY', 'SENDER_FROM_ADDRESS', 'RECIPIENT_EMAIL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ 缺少必要的环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("示例设置方式：")
        print("  set RESEND_API_KEY=re_your_api_key")
        print("  set SENDER_FROM_ADDRESS=测试 <alerts@your-domain.com>")
        print("  set RECIPIENT_EMAIL=your@email.com")
        print()
        response = input("是否继续（部分功能不可用）？: ")
        if response.lower() != 'y':
            return False
    else:
        print("✅ 环境变量配置完整")
    print()

    return True

def create_temp_data_dir():
    """创建临时测试数据目录"""
    temp_dir = tempfile.mkdtemp(prefix="power_monitor_test_")
    print(f"📁 创建临时测试目录: {temp_dir}")
    return temp_dir

def test_1_send_test_email():
    """测试1: 发送测试邮件"""
    print("\n" + "=" * 60)
    print("测试 1: 发送测试邮件")
    print("=" * 60)

    if not os.getenv('RESEND_API_KEY'):
        print("⚠️  跳过：缺少 RESEND_API_KEY")
        return

    try:
        import resend
        resend.api_key = os.getenv('RESEND_API_KEY')

        params = {
            "from": os.getenv('SENDER_FROM_ADDRESS', 'Test <test@example.com>'),
            "to": [os.getenv('RECIPIENT_EMAIL', 'test@example.com>')],
            "subject": f"[测试] 电力监控系统测试邮件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "html": """
            <html><body>
                <h2>📧 测试邮件</h2>
                <p>如果你收到这封邮件，说明邮件发送功能正常！</p>
                <hr>
                <p><strong>测试时间:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                <p><strong>测试场景:</strong> 基本邮件发送测试</p>
            </body></html>
            """
        }

        print("📤 正在发送邮件...")
        result = resend.Emails.send(params)
        print(f"✅ 邮件发送成功！Email ID: {result.get('id', 'N/A')}")
        print(f"📬 请检查收件箱: {os.getenv('RECIPIENT_EMAIL')}")

    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

def test_2_simulate_power_outage(temp_dir):
    """测试2: 模拟断电"""
    print("\n" + "=" * 60)
    print("测试 2: 模拟断电场景")
    print("=" * 60)

    from app import main

    # 修改模块常量指向临时目录
    original_heartbeat_a = main.HEARTBEAT_FILE_A
    original_heartbeat_b = main.HEARTBEAT_FILE_B
    original_network_status = main.NETWORK_STATUS_FILE
    original_network_history = main.NETWORK_HISTORY_FILE
    original_pending = main.PENDING_NOTIFICATIONS_FILE

    main.HEARTBEAT_FILE_A = os.path.join(temp_dir, "heartbeat_a.log")
    main.HEARTBEAT_FILE_B = os.path.join(temp_dir, "heartbeat_b.log")
    main.NETWORK_STATUS_FILE = os.path.join(temp_dir, "network_status.log")
    main.NETWORK_HISTORY_FILE = os.path.join(temp_dir, "network_history.log")
    main.PENDING_NOTIFICATIONS_FILE = os.path.join(temp_dir, "pending_notifications.log")

    try:
        # 创建5分钟前的心跳文件（模拟断电）
        outage_time = int(time.time()) - 300  # 5分钟前
        with open(main.HEARTBEAT_FILE_A, 'w') as f:
            f.write(str(outage_time))
        with open(main.HEARTBEAT_FILE_B, 'w') as f:
            f.write(str(outage_time))

        # 创建网络状态文件
        network_status = {
            "timestamp": int(time.time()),
            "internal_network": True,
            "external_network": True,
            "dns_resolution": True
        }
        with open(main.NETWORK_STATUS_FILE, 'w') as f:
            json.dump(network_status, f)

        # 创建网络历史文件
        network_history = {
            "last_internal_network": True,
            "last_external_network": True
        }
        with open(main.NETWORK_HISTORY_FILE, 'w') as f:
            json.dump(network_history, f)

        print(f"📝 创建心跳文件: {datetime.fromtimestamp(outage_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print("⚡ 模拟断电: 5分钟前")
        print("🔧 运行 main.py 检测...")

        # 运行 main.py
        main.main()

        # 检查是否生成了待发送通知
        if os.path.exists(main.PENDING_NOTIFICATIONS_FILE):
            with open(main.PENDING_NOTIFICATIONS_FILE, 'r') as f:
                notifications = json.load(f)
            print(f"✅ 检测到断电！已生成 {len(notifications)} 个待发送通知")
            if notifications:
                print(f"📧 通知类型: {notifications[0].get('type', 'N/A')}")
                print(f"⏱️  断电时长: {notifications[0].get('duration_formatted', 'N/A')}")
        else:
            print("⚠️  未检测到断电（可能未超过阈值）")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 恢复原始常量
        main.HEARTBEAT_FILE_A = original_heartbeat_a
        main.HEARTBEAT_FILE_B = original_heartbeat_b
        main.NETWORK_STATUS_FILE = original_network_status
        main.NETWORK_HISTORY_FILE = original_network_history
        main.PENDING_NOTIFICATIONS_FILE = original_pending

def test_3_simulate_network_outage(temp_dir):
    """测试3: 模拟断网"""
    print("\n" + "=" * 60)
    print("测试 3: 模拟断网场景")
    print("=" * 60)

    from app import main

    # 修改模块常量
    original_heartbeat_a = main.HEARTBEAT_FILE_A
    original_heartbeat_b = main.HEARTBEAT_FILE_B
    original_network_status = main.NETWORK_STATUS_FILE
    original_network_history = main.NETWORK_HISTORY_FILE
    original_pending = main.PENDING_NOTIFICATIONS_FILE

    main.HEARTBEAT_FILE_A = os.path.join(temp_dir, "heartbeat_a.log")
    main.HEARTBEAT_FILE_B = os.path.join(temp_dir, "heartbeat_b.log")
    main.NETWORK_STATUS_FILE = os.path.join(temp_dir, "network_status.log")
    main.NETWORK_HISTORY_FILE = os.path.join(temp_dir, "network_history.log")
    main.PENDING_NOTIFICATIONS_FILE = os.path.join(temp_dir, "pending_notifications.log")

    try:
        # 创建当前时间的心跳文件（正常）
        current_time = int(time.time())
        with open(main.HEARTBEAT_FILE_A, 'w') as f:
            f.write(str(current_time))
        with open(main.HEARTBEAT_FILE_B, 'w') as f:
            f.write(str(current_time))

        # 创建网络状态文件（内网正常，外网断开）
        network_status = {
            "timestamp": int(time.time()),
            "internal_network": True,
            "external_network": False,  # 外网断开
            "dns_resolution": False
        }
        with open(main.NETWORK_STATUS_FILE, 'w') as f:
            json.dump(network_status, f)

        # 创建网络历史文件（之前都正常）
        network_history = {
            "last_internal_network": True,
            "last_external_network": True  # 之前外网正常
        }
        with open(main.NETWORK_HISTORY_FILE, 'w') as f:
            json.dump(network_history, f)

        print(f"📝 创建心跳文件: {datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print("🌐 模拟网络状态:")
        print("   - 内网: ✅ 正常")
        print("   - 外网: ❌ 断开")
        print("   - DNS: ❌ 异常")
        print("🔧 运行 main.py 检测...")

        # 运行 main.py
        main.main()

        print("✅ 断网检测测试完成")
        print("💡 提示: 请检查是否收到网络状态变化通知邮件")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 恢复原始常量
        main.HEARTBEAT_FILE_A = original_heartbeat_a
        main.HEARTBEAT_FILE_B = original_heartbeat_b
        main.NETWORK_STATUS_FILE = original_network_status
        main.NETWORK_HISTORY_FILE = original_network_history
        main.PENDING_NOTIFICATIONS_FILE = original_pending

def test_4_send_pending_notifications(temp_dir):
    """测试4: 发送待处理通知"""
    print("\n" + "=" * 60)
    print("测试 4: 发送待处理通知")
    print("=" * 60)

    if not os.getenv('RESEND_API_KEY'):
        print("⚠️  跳过：缺少 RESEND_API_KEY")
        return

    from app import heartbeat

    # 修改模块常量
    original_pending = heartbeat.PENDING_NOTIFICATIONS_FILE
    original_network_status = heartbeat.NETWORK_STATUS_FILE

    heartbeat.PENDING_NOTIFICATIONS_FILE = os.path.join(temp_dir, "pending_notifications.log")
    heartbeat.NETWORK_STATUS_FILE = os.path.join(temp_dir, "network_status.log")

    try:
        # 创建测试通知
        test_notification = {
            "type": "power_outage",
            "timestamp": int(time.time()),
            "power_off_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "power_on_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "duration_formatted": "00 小时 05 分钟 00 秒",
            "subject": "[断电警报] 服务器 测试服务器 发生异常断电",
            "html_body": "<html><body><h2>测试断电通知</h2></body></html>"
        }

        with open(heartbeat.PENDING_NOTIFICATIONS_FILE, 'w') as f:
            json.dump([test_notification], f)

        # 创建网络状态（外网正常）
        network_status = {
            "timestamp": int(time.time()),
            "internal_network": True,
            "external_network": True,  # 外网正常，可以发送
            "dns_resolution": True
        }
        with open(heartbeat.NETWORK_STATUS_FILE, 'w') as f:
            json.dump(network_status, f)

        print("📋 创建待发送通知...")
        print("🌐 模拟网络恢复（外网正常）")
        print("📤 尝试发送待处理通知...")

        # 发送待处理通知
        heartbeat.process_pending_notifications()

        print("✅ 待处理通知发送完成")
        print("💡 提示: 请检查收件箱是否收到断电通知邮件")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 恢复原始常量
        heartbeat.PENDING_NOTIFICATIONS_FILE = original_pending
        heartbeat.NETWORK_STATUS_FILE = original_network_status

def cleanup_temp_dir(temp_dir):
    """清理临时目录"""
    print("\n" + "=" * 60)
    print("清理临时目录")
    print("=" * 60)

    # 询问是否保留
    response = input(f"是否保留临时目录用于调试？\n路径: {temp_dir}\n: ")
    if response.lower() != 'y':
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"🗑️  已删除临时目录: {temp_dir}")
    else:
        print(f"📁 保留临时目录: {temp_dir}")

def main_menu():
    """主菜单"""
    print("\n" + "🔋" * 30)
    print("     电力监控系统 - 场景测试工具")
    print("🔋" * 30)

    print("\n可用测试场景:")
    print("  1. 发送测试邮件")
    print("  2. 模拟断电场景")
    print("  3. 模拟断网场景")
    print("  4. 发送待处理通知")
    print("  5. 运行所有测试")
    print("  0. 退出")

    choice = input("\n请选择测试场景 (0-5): ").strip()

    return choice

if __name__ == "__main__":
    # 设置环境
    if not setup_environment():
        print("❌ 无法继续测试")
        sys.exit(1)

    # 创建临时目录
    temp_dir = create_temp_data_dir()

    try:
        # 主菜单
        while True:
            choice = main_menu()

            if choice == '0':
                print("\n👋 退出测试")
                break
            elif choice == '1':
                test_1_send_test_email()
            elif choice == '2':
                test_2_simulate_power_outage(temp_dir)
            elif choice == '3':
                test_3_simulate_network_outage(temp_dir)
            elif choice == '4':
                test_4_send_pending_notifications(temp_dir)
            elif choice == '5':
                print("\n🚀 运行所有测试...")
                test_1_send_test_email()
                test_2_simulate_power_outage(temp_dir)
                test_3_simulate_network_outage(temp_dir)
                test_4_send_pending_notifications(temp_dir)
            else:
                print("\n❌ 无效选择，请重试")

            # 询问是否继续
            if choice != '0':
                input("\n按 Enter 继续...")

    finally:
        # 清理
        cleanup_temp_dir(temp_dir)

    print("\n✅ 测试完成！")