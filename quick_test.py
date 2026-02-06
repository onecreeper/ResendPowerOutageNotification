#!/usr/bin/env python
"""
快速测试脚本 - 无需交互
自动运行基本的场景测试
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

def check_environment():
    """检查环境变量"""
    print("=" * 60)
    print("检查环境配置")
    print("=" * 60)

    required_vars = ['RESEND_API_KEY', 'SENDER_FROM_ADDRESS', 'RECIPIENT_EMAIL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("⚠️  将跳过邮件发送测试")
        return False

    print("✅ 环境变量配置完整")
    return True

def run_tests():
    """运行所有测试"""
    has_env = check_environment()
    temp_dir = tempfile.mkdtemp(prefix="power_monitor_test_")

    try:
        print(f"\n📁 临时目录: {temp_dir}\n")

        # 测试 1: 模拟断电（不需要邮件）
        print("=" * 60)
        print("测试 1: 模拟断电场景")
        print("=" * 60)

        from app import main

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
            # 创建5分钟前的心跳文件
            outage_time = int(time.time()) - 300
            with open(main.HEARTBEAT_FILE_A, 'w') as f:
                f.write(str(outage_time))
            with open(main.HEARTBEAT_FILE_B, 'w') as f:
                f.write(str(outage_time))

            # 创建网络状态
            network_status = {
                "timestamp": int(time.time()),
                "internal_network": True,
                "external_network": True,
                "dns_resolution": True
            }
            with open(main.NETWORK_STATUS_FILE, 'w') as f:
                json.dump(network_status, f)

            network_history = {
                "last_internal_network": True,
                "last_external_network": True
            }
            with open(main.NETWORK_HISTORY_FILE, 'w') as f:
                json.dump(network_history, f)

            print("⚡ 模拟断电: 5分钟前")
            print("🔧 运行检测...")
            main.main()

            # 检查结果
            if os.path.exists(main.PENDING_NOTIFICATIONS_FILE):
                with open(main.PENDING_NOTIFICATIONS_FILE, 'r') as f:
                    notifications = json.load(f)
                print(f"✅ 检测到断电，生成 {len(notifications)} 个通知")
                if notifications:
                    print(f"   断电时长: {notifications[0].get('duration_formatted', 'N/A')}")
            else:
                print("⚠️  未检测到断电")

        finally:
            main.HEARTBEAT_FILE_A = original_heartbeat_a
            main.HEARTBEAT_FILE_B = original_heartbeat_b
            main.NETWORK_STATUS_FILE = original_network_status
            main.NETWORK_HISTORY_FILE = original_network_history
            main.PENDING_NOTIFICATIONS_FILE = original_pending

        # 测试 2: 模拟断网（不需要邮件）
        print("\n" + "=" * 60)
        print("测试 2: 模拟断网场景")
        print("=" * 60)

        main.HEARTBEAT_FILE_A = os.path.join(temp_dir, "heartbeat_a.log")
        main.HEARTBEAT_FILE_B = os.path.join(temp_dir, "heartbeat_b.log")
        main.NETWORK_STATUS_FILE = os.path.join(temp_dir, "network_status2.log")
        main.NETWORK_HISTORY_FILE = os.path.join(temp_dir, "network_history2.log")
        main.PENDING_NOTIFICATIONS_FILE = os.path.join(temp_dir, "pending_notifications2.log")

        try:
            # 创建当前心跳
            current_time = int(time.time())
            with open(main.HEARTBEAT_FILE_A, 'w') as f:
                f.write(str(current_time))
            with open(main.HEARTBEAT_FILE_B, 'w') as f:
                f.write(str(current_time))

            # 网络断开状态
            network_status = {
                "timestamp": int(time.time()),
                "internal_network": True,
                "external_network": False,
                "dns_resolution": False
            }
            with open(main.NETWORK_STATUS_FILE, 'w') as f:
                json.dump(network_status, f)

            network_history = {
                "last_internal_network": True,
                "last_external_network": True
            }
            with open(main.NETWORK_HISTORY_FILE, 'w') as f:
                json.dump(network_history, f)

            print("🌐 模拟断网: 外网断开")
            print("🔧 运行检测...")
            main.main()
            print("✅ 断网检测完成")

        finally:
            main.HEARTBEAT_FILE_A = original_heartbeat_a
            main.HEARTBEAT_FILE_B = original_heartbeat_b
            main.NETWORK_STATUS_FILE = original_network_status
            main.NETWORK_HISTORY_FILE = original_network_history
            main.PENDING_NOTIFICATIONS_FILE = original_pending

        # 测试 3: 发送邮件（需要环境变量）
        if has_env:
            print("\n" + "=" * 60)
            print("测试 3: 发送测试邮件")
            print("=" * 60)

            try:
                import resend
                resend.api_key = os.getenv('RESEND_API_KEY')

                params = {
                    "from": os.getenv('SENDER_FROM_ADDRESS'),
                    "to": [os.getenv('RECIPIENT_EMAIL')],
                    "subject": f"[测试] 电力监控系统 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "html": """
                    <html><body>
                        <h2>✅ 测试邮件</h2>
                        <p>电力监控系统邮件发送功能正常！</p>
                        <hr>
                        <p><strong>测试时间:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                        <p><strong>测试场景:</strong> 快速自动化测试</p>
                    </body></html>
                    """
                }

                print("📤 发送邮件...")
                result = resend.Emails.send(params)
                print(f"✅ 邮件发送成功！ID: {result.get('id', 'N/A')}")
                print(f"📬 收件人: {os.getenv('RECIPIENT_EMAIL')}")

            except Exception as e:
                print(f"❌ 邮件发送失败: {e}")
        else:
            print("\n" + "=" * 60)
            print("测试 3: 发送测试邮件")
            print("=" * 60)
            print("⚠️  跳过：未配置环境变量")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        print(f"📁 临时目录: {temp_dir}")
        print("💡 提示: 临时目录将在 30 秒后自动删除...")

        # 30秒后删除
        time.sleep(30)
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("🗑️  已删除临时目录")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(0)
