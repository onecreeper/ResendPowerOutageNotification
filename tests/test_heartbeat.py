import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock, call
import subprocess
import time
import socket


class TestHeartbeatFunctionality:
    """测试 heartbeat.py 的核心功能"""

    def test_get_network_targets_default(self, mock_env_vars):
        """测试获取默认网络检测目标"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        # 清除环境变量以使用默认值
        os.environ.pop("INTERNAL_TARGETS", None)
        os.environ.pop("EXTERNAL_TARGETS", None)
        os.environ.pop("DNS_TARGET", None)

        targets = heartbeat.get_network_targets()

        assert "internal" in targets
        assert "external" in targets
        assert "dns" in targets
        assert len(targets["internal"]) == 2
        assert len(targets["external"]) == 3
        assert targets["dns"] == "baidu.com"

    def test_get_network_targets_custom(self, mock_env_vars):
        """测试获取自定义网络检测目标"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        os.environ["INTERNAL_TARGETS"] = "192.168.1.100,192.168.2.1"
        os.environ["EXTERNAL_TARGETS"] = "8.8.8.8,google.com"
        os.environ["DNS_TARGET"] = "example.com"

        targets = heartbeat.get_network_targets()

        assert targets["internal"] == ["192.168.1.100", "192.168.2.1"]
        assert targets["external"] == ["8.8.8.8", "google.com"]
        assert targets["dns"] == "example.com"

    def test_get_network_targets_empty_custom(self, mock_env_vars):
        """测试自定义目标为空时使用默认值"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        os.environ["INTERNAL_TARGETS"] = ""
        os.environ["EXTERNAL_TARGETS"] = ""

        targets = heartbeat.get_network_targets()

        # 应该使用默认值
        assert len(targets["internal"]) > 0
        assert len(targets["external"]) > 0

    def test_save_network_status(self, temp_data_dir):
        """测试保存网络状态"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        test_file = os.path.join(temp_data_dir, "network_status.log")
        test_status = {
            "timestamp": int(time.time()),
            "internal_network": True,
            "external_network": False,
            "dns_resolution": True
        }

        original_file = heartbeat.NETWORK_STATUS_FILE
        heartbeat.NETWORK_STATUS_FILE = test_file
        
        try:
            heartbeat.save_network_status(test_status)

            # 验证保存
            with open(test_file, 'r') as f:
                loaded_status = json.load(f)
            assert loaded_status == test_status
        finally:
            heartbeat.NETWORK_STATUS_FILE = original_file

    def test_load_pending_notifications_empty(self, temp_data_dir):
        """测试加载空的待发送通知"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        test_file = os.path.join(temp_data_dir, "pending_notifications.log")
        original_file = heartbeat.PENDING_NOTIFICATIONS_FILE
        heartbeat.PENDING_NOTIFICATIONS_FILE = test_file
        
        try:
            notifications = heartbeat._load_pending_notifications()
            assert notifications == []
        finally:
            heartbeat.PENDING_NOTIFICATIONS_FILE = original_file

    def test_save_pending_notifications(self, temp_data_dir):
        """测试保存待发送通知"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        test_file = os.path.join(temp_data_dir, "pending_notifications.log")
        test_data = [
            {
                "type": "test",
                "subject": "Test Subject",
                "html_body": "<html>Test</html>"
            }
        ]

        original_file = heartbeat.PENDING_NOTIFICATIONS_FILE
        heartbeat.PENDING_NOTIFICATIONS_FILE = test_file
        
        try:
            heartbeat._save_pending_notifications(test_data)

            with open(test_file, 'r') as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data
        finally:
            heartbeat.PENDING_NOTIFICATIONS_FILE = original_file

    def test_send_email_with_resend_success(self, mock_env_vars):
        """测试成功发送邮件"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        with patch('resend.Emails.send') as mock_resend:
            mock_resend.return_value = {"id": "test_email_id"}

            result = heartbeat.send_email_with_resend(
                "Test Subject",
                "<html><body>Test</body></html>"
            )

            assert result == True
            mock_resend.assert_called_once()

    def test_send_email_with_resend_missing_config(self):
        """测试缺少邮件配置时"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        # 清除环境变量
        os.environ.pop("RESEND_API_KEY", None)
        os.environ.pop("SENDER_FROM_ADDRESS", None)
        os.environ.pop("RECIPIENT_EMAIL", None)

        result = heartbeat.send_email_with_resend(
            "Test Subject",
            "<html>Test</html>"
        )

        assert result == False

    def test_send_email_with_resend_api_error(self, mock_env_vars):
        """测试 Resend API 错误"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        with patch('resend.Emails.send') as mock_resend:
            mock_resend.side_effect = Exception("API Error")

            result = heartbeat.send_email_with_resend(
                "Test Subject",
                "<html>Test</html>"
            )

            assert result == False

    def test_process_pending_notifications_empty(self, temp_data_dir):
        """测试处理空的待发送通知队列"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        test_file = os.path.join(temp_data_dir, "pending_notifications.log")
        original_file = heartbeat.PENDING_NOTIFICATIONS_FILE
        heartbeat.PENDING_NOTIFICATIONS_FILE = test_file
        
        try:
            with patch('app.heartbeat.send_email_with_resend') as mock_send:
                heartbeat.process_pending_notifications()

                mock_send.assert_not_called()
        finally:
            heartbeat.PENDING_NOTIFICATIONS_FILE = original_file

    def test_process_pending_notifications_success(self, temp_data_dir):
        """测试成功处理待发送通知"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        test_file = os.path.join(temp_data_dir, "pending_notifications.log")
        test_notifications = [
            {
                "type": "power_outage",
                "subject": "Test Subject 1",
                "html_body": "<html>Test 1</html>"
            },
            {
                "type": "network_issue",
                "subject": "Test Subject 2",
                "html_body": "<html>Test 2</html>"
            }
        ]

        with open(test_file, 'w') as f:
            json.dump(test_notifications, f)

        original_file = heartbeat.PENDING_NOTIFICATIONS_FILE
        heartbeat.PENDING_NOTIFICATIONS_FILE = test_file
        
        try:
            with patch('app.heartbeat.send_email_with_resend', return_value=True) as mock_send:
                heartbeat.process_pending_notifications()

                assert mock_send.call_count == 2
        finally:
            heartbeat.PENDING_NOTIFICATIONS_FILE = original_file

    def test_process_pending_notifications_partial_failure(self, temp_data_dir):
        """测试部分通知发送失败"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        test_file = os.path.join(temp_data_dir, "pending_notifications.log")
        test_notifications = [
            {
                "type": "test1",
                "subject": "Success",
                "html_body": "<html>Success</html>"
            },
            {
                "type": "test2",
                "subject": "Failed",
                "html_body": "<html>Failed</html>"
            }
        ]

        with open(test_file, 'w') as f:
            json.dump(test_notifications, f)

        original_file = heartbeat.PENDING_NOTIFICATIONS_FILE
        heartbeat.PENDING_NOTIFICATIONS_FILE = test_file
        
        try:
            def send_side_effect(subject, body):
                return "Success" in subject

            with patch('app.heartbeat.send_email_with_resend', side_effect=send_side_effect) as mock_send:
                heartbeat.process_pending_notifications()

                # 验证重试的队列只包含失败的通知
                remaining = heartbeat._load_pending_notifications()
                assert len(remaining) == 1
                assert remaining[0]["subject"] == "Failed"
        finally:
            heartbeat.PENDING_NOTIFICATIONS_FILE = original_file

    def test_check_and_send_pending_notifications_with_network(self, temp_data_dir):
        """测试有网络时发送待处理通知"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        test_file = os.path.join(temp_data_dir, "pending_notifications.log")
        test_notifications = [
            {
                "type": "test",
                "subject": "Test",
                "html_body": "<html>Test</html>"
            }
        ]

        with open(test_file, 'w') as f:
            json.dump(test_notifications, f)

        network_status = {
            "external_network": True,
            "internal_network": True,
            "dns_resolution": True
        }

        with patch('app.heartbeat.process_pending_notifications') as mock_process:
            heartbeat.check_and_send_pending_notifications(network_status)

            mock_process.assert_called_once()

    def test_check_and_send_pending_notifications_without_network(self, temp_data_dir):
        """测试无网络时不发送通知"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        test_file = os.path.join(temp_data_dir, "pending_notifications.log")
        test_notifications = [
            {
                "type": "test",
                "subject": "Test",
                "html_body": "<html>Test</html>"
            }
        ]

        with open(test_file, 'w') as f:
            json.dump(test_notifications, f)

        network_status = {
            "external_network": False,
            "internal_network": True,
            "dns_resolution": True
        }

        with patch('app.heartbeat.process_pending_notifications') as mock_process:
            heartbeat.check_and_send_pending_notifications(network_status)

            mock_process.assert_not_called()

    @patch('subprocess.run')
    @patch('socket.gethostbyname')
    def test_check_network_connectivity_all_up(self, mock_dns, mock_ping, mock_env_vars):
        """测试所有网络连接正常"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        # Mock DNS 解析成功
        mock_dns.return_value = "1.2.3.4"

        # Mock ping 成功
        mock_ping.return_value = MagicMock(returncode=0)

        status = heartbeat.check_network_connectivity()

        assert status["dns_resolution"] == True
        assert status["internal_network"] == True
        assert status["external_network"] == True

    @patch('subprocess.run')
    @patch('socket.gethostbyname')
    def test_check_network_connectivity_dns_down(self, mock_dns, mock_ping, mock_env_vars):
        """测试 DNS 解析失败"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        # Mock DNS 解析失败
        mock_dns.side_effect = socket.gaierror("DNS resolution failed")

        status = heartbeat.check_network_connectivity()

        assert status["dns_resolution"] == False

    @patch('subprocess.run')
    @patch('socket.gethostbyname')
    def test_check_network_connectivity_internal_down(self, mock_dns, mock_ping, mock_env_vars):
        """测试内网连接失败"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        # Mock DNS 成功
        mock_dns.return_value = "1.2.3.4"

        # Mock ping 失败
        mock_ping.return_value = MagicMock(returncode=1)

        status = heartbeat.check_network_connectivity()

        assert status["dns_resolution"] == True
        assert status["internal_network"] == False

    @patch('subprocess.run')
    @patch('socket.gethostbyname')
    def test_check_network_connectivity_timeout(self, mock_dns, mock_ping, mock_env_vars):
        """测试网络连接超时"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import heartbeat

        mock_dns.return_value = "1.2.3.4"

        # Mock ping 超时
        mock_ping.side_effect = subprocess.TimeoutExpired("ping", 5)

        status = heartbeat.check_network_connectivity()

        # 应该继续尝试下一个主机
        assert "timestamp" in status