import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import time


class TestMainFunctionality:
    """测试 main.py 的核心功能"""

    def test_get_valid_timestamp_valid_file(self, temp_data_dir):
        """测试读取有效的时间戳文件"""
        # 导入 main 模块的函数
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        # 创建测试文件
        test_file = os.path.join(temp_data_dir, "test_timestamp.log")
        test_timestamp = int(time.time())
        with open(test_file, 'w') as f:
            f.write(str(test_timestamp))

        # 测试读取
        timestamp, status = main._get_valid_timestamp(test_file)
        assert timestamp == test_timestamp
        assert status == "valid"

    def test_get_valid_timestamp_empty_file(self, temp_data_dir):
        """测试读取空文件"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        test_file = os.path.join(temp_data_dir, "test_empty.log")
        with open(test_file, 'w') as f:
            f.write("")

        timestamp, status = main._get_valid_timestamp(test_file)
        assert timestamp is None
        assert status == "empty"

    def test_get_valid_timestamp_nonexistent_file(self):
        """测试读取不存在的文件"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        timestamp, status = main._get_valid_timestamp("/nonexistent/path/file.log")
        assert timestamp is None
        assert status == "non-existent"

    def test_get_valid_timestamp_corrupted_file(self, temp_data_dir):
        """测试读取损坏的文件"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        test_file = os.path.join(temp_data_dir, "test_corrupted.log")
        with open(test_file, 'w') as f:
            f.write("not_a_number")

        timestamp, status = main._get_valid_timestamp(test_file)
        assert timestamp is None
        assert status == "corrupted"

    def test_write_timestamp(self, temp_data_dir):
        """测试写入时间戳"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        test_file = os.path.join(temp_data_dir, "test_write.log")
        test_timestamp = int(time.time())

        main._write_timestamp(test_file, test_timestamp)

        # 验证写入
        with open(test_file, 'r') as f:
            written_timestamp = int(f.read().strip())
        assert written_timestamp == test_timestamp

    def test_remove_file(self, temp_data_dir):
        """测试删除文件"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        test_file = os.path.join(temp_data_dir, "test_remove.log")
        with open(test_file, 'w') as f:
            f.write("test")

        assert os.path.exists(test_file)
        main._remove_file(test_file)
        assert not os.path.exists(test_file)

    def test_load_network_status(self, temp_data_dir):
        """测试加载网络状态"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        # 创建测试文件路径
        test_file = os.path.join(temp_data_dir, "network_status.log")
        
        # 写入测试数据
        test_data = {
            "timestamp": int(time.time()),
            "internal_network": True,
            "external_network": False,
            "dns_resolution": True
        }
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        # 临时修改模块常量
        original_file = main.NETWORK_STATUS_FILE
        main.NETWORK_STATUS_FILE = test_file
        
        try:
            # 读取测试
            loaded_data = main._load_network_status()
            assert loaded_data == test_data
        finally:
            # 恢复原始值
            main.NETWORK_STATUS_FILE = original_file

    def test_load_network_status_nonexistent(self, temp_data_dir):
        """测试加载不存在的网络状态文件"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        # 使用不存在的路径
        original_file = main.NETWORK_STATUS_FILE
        main.NETWORK_STATUS_FILE = os.path.join(temp_data_dir, "nonexistent.log")
        
        try:
            result = main._load_network_status()
            assert result is None
        finally:
            main.NETWORK_STATUS_FILE = original_file

    def test_load_network_history(self, temp_data_dir):
        """测试加载网络历史记录"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        test_file = os.path.join(temp_data_dir, "network_history.log")
        test_data = {
            "last_internal_network": True,
            "last_external_network": False
        }
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        original_file = main.NETWORK_HISTORY_FILE
        main.NETWORK_HISTORY_FILE = test_file
        
        try:
            loaded_data = main._load_network_history()
            assert loaded_data == test_data
        finally:
            main.NETWORK_HISTORY_FILE = original_file

    def test_save_network_history(self, temp_data_dir):
        """测试保存网络历史记录"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        test_file = os.path.join(temp_data_dir, "network_history.log")
        test_data = {
            "last_internal_network": False,
            "last_external_network": True
        }
        
        original_file = main.NETWORK_HISTORY_FILE
        main.NETWORK_HISTORY_FILE = test_file
        
        try:
            main._save_network_history(test_data)

            # 验证保存
            with open(test_file, 'r') as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data
        finally:
            main.NETWORK_HISTORY_FILE = original_file

    def test_load_pending_notifications(self, temp_data_dir):
        """测试加载待发送通知"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        test_file = os.path.join(temp_data_dir, "pending_notifications.log")
        test_data = [
            {
                "type": "power_outage",
                "timestamp": int(time.time()),
                "subject": "Test",
                "html_body": "<html></html>"
            }
        ]
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        original_file = main.PENDING_NOTIFICATIONS_FILE
        main.PENDING_NOTIFICATIONS_FILE = test_file
        
        try:
            loaded_data = main._load_pending_notifications()
            assert len(loaded_data) == 1
            assert loaded_data[0]["type"] == "power_outage"
        finally:
            main.PENDING_NOTIFICATIONS_FILE = original_file

    def test_save_pending_notifications(self, temp_data_dir):
        """测试保存待发送通知"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        test_file = os.path.join(temp_data_dir, "pending_notifications.log")
        test_data = [
            {
                "type": "test",
                "timestamp": int(time.time()),
                "subject": "Test Subject",
                "html_body": "<html>Test</html>"
            }
        ]
        
        original_file = main.PENDING_NOTIFICATIONS_FILE
        main.PENDING_NOTIFICATIONS_FILE = test_file
        
        try:
            main._save_pending_notifications(test_data)

            # 验证保存
            with open(test_file, 'r') as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data
        finally:
            main.PENDING_NOTIFICATIONS_FILE = original_file

    def test_add_pending_notification(self, temp_data_dir):
        """测试添加待发送通知"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        test_file = os.path.join(temp_data_dir, "pending_notifications.log")
        notification = {
            "type": "test",
            "timestamp": int(time.time()),
            "subject": "Test",
            "html_body": "<html>Test</html>"
        }

        original_file = main.PENDING_NOTIFICATIONS_FILE
        main.PENDING_NOTIFICATIONS_FILE = test_file
        
        try:
            main._add_pending_notification(notification)

            loaded_data = main._load_pending_notifications()
            assert len(loaded_data) == 1
            assert loaded_data[0] == notification
        finally:
            main.PENDING_NOTIFICATIONS_FILE = original_file

    @patch('app.main.send_email_with_resend')
    def test_check_network_status_changes_no_change(self, mock_send_email, network_status_file, network_history_file):
        """测试网络状态无变化的情况"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        # 创建相同的当前和历史状态
        current_status = {
            "timestamp": int(time.time()),
            "internal_network": True,
            "external_network": True,
            "dns_resolution": True
        }
        history = {
            "last_internal_network": True,
            "last_external_network": True
        }

        with open(network_status_file, 'w') as f:
            json.dump(current_status, f)
        with open(network_history_file, 'w') as f:
            json.dump(history, f)

        main.check_network_status_changes()

        # 验证没有发送邮件
        mock_send_email.assert_not_called()

    @patch('app.main.send_email_with_resend')
    def test_check_network_status_changes_internal_down(self, mock_send_email, temp_data_dir):
        """测试内网中断的情况"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        test_status_file = os.path.join(temp_data_dir, "network_status.log")
        test_history_file = os.path.join(temp_data_dir, "network_history.log")
        
        current_status = {
            "timestamp": int(time.time()),
            "internal_network": False,
            "external_network": True,
            "dns_resolution": True
        }
        history = {
            "last_internal_network": True,
            "last_external_network": True
        }

        with open(test_status_file, 'w') as f:
            json.dump(current_status, f)
        with open(test_history_file, 'w') as f:
            json.dump(history, f)

        original_status_file = main.NETWORK_STATUS_FILE
        original_history_file = main.NETWORK_HISTORY_FILE
        
        main.NETWORK_STATUS_FILE = test_status_file
        main.NETWORK_HISTORY_FILE = test_history_file
        
        try:
            main.check_network_status_changes()

            # 验证发送了邮件
            mock_send_email.assert_called_once()

            # 验证历史记录已更新
            updated_history = main._load_network_history()
            assert updated_history["last_internal_network"] == False
        finally:
            main.NETWORK_STATUS_FILE = original_status_file
            main.NETWORK_HISTORY_FILE = original_history_file

    @patch('app.main.send_email_with_resend')
    def test_check_network_status_changes_expired_data(self, mock_send_email, temp_data_dir):
        """测试网络状态数据过期的情况"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        test_status_file = os.path.join(temp_data_dir, "network_status.log")
        test_history_file = os.path.join(temp_data_dir, "network_history.log")
        
        # 创建过期的状态数据（6分钟前）
        current_status = {
            "timestamp": int(time.time()) - 360,
            "internal_network": False,
            "external_network": True,
            "dns_resolution": True
        }
        history = {
            "last_internal_network": True,
            "last_external_network": True
        }

        with open(test_status_file, 'w') as f:
            json.dump(current_status, f)
        with open(test_history_file, 'w') as f:
            json.dump(history, f)

        original_status_file = main.NETWORK_STATUS_FILE
        original_history_file = main.NETWORK_HISTORY_FILE
        
        main.NETWORK_STATUS_FILE = test_status_file
        main.NETWORK_HISTORY_FILE = test_history_file
        
        try:
            main.check_network_status_changes()

            # 验证没有发送邮件（数据过期）
            mock_send_email.assert_not_called()
        finally:
            main.NETWORK_STATUS_FILE = original_status_file
            main.NETWORK_HISTORY_FILE = original_history_file

    def test_send_network_status_email(self):
        """测试发送网络状态变化邮件"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        current_status = {
            "timestamp": int(time.time()),
            "internal_network": False,
            "external_network": True,
            "dns_resolution": True
        }
        previous_status = {
            "last_internal_network": True,
            "last_external_network": True
        }

        with patch('app.main.send_email_with_resend') as mock_send:
            main.send_network_status_email(current_status, previous_status)

            # 验证调用参数
            assert mock_send.called
            args, kwargs = mock_send.call_args
            subject = args[0]
            html_body = args[1]

            assert "网络状态" in subject
            assert "内网连接" in html_body
            assert "外网连接" in html_body

    @patch('app.main._add_pending_notification')
    def test_main_power_outage_detected(self, mock_add_notification, heartbeat_files):
        """测试检测到断电的情况"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import main

        file_a, file_b = heartbeat_files

        # 设置环境变量
        os.environ["RESEND_API_KEY"] = "test_key"
        os.environ["SENDER_FROM_ADDRESS"] = "test@example.com"
        os.environ["RECIPIENT_EMAIL"] = "recipient@example.com"
        os.environ["SERVER_NAME"] = "Test Server"
        os.environ["OUTAGE_THRESHOLD"] = "180"

        # 创建5分钟前的心跳文件
        old_timestamp = int(time.time()) - 300
        with open(file_a, 'w') as f:
            f.write(str(old_timestamp))
        with open(file_b, 'w') as f:
            f.write(str(old_timestamp))

        # 模拟 main 函数中的常量
        main.HEARTBEAT_FILE_A = file_a
        main.HEARTBEAT_FILE_B = file_b
        main.NETWORK_STATUS_FILE = os.path.join(os.path.dirname(file_a), "network_status.log")
        main.NETWORK_HISTORY_FILE = os.path.join(os.path.dirname(file_a), "network_history.log")
        main.PENDING_NOTIFICATIONS_FILE = os.path.join(os.path.dirname(file_a), "pending_notifications.log")

        with patch('app.main.check_network_status_changes'):
            main.main()

        # 验证添加了待发送通知
        mock_add_notification.assert_called_once()