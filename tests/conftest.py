import pytest
import os
import tempfile
import shutil
from datetime import datetime
import time
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True, scope="session")
def setup_resend_mock():
    """在整个测试会话中 mock resend 模块"""
    import sys
    
    # 创建 mock 模块
    mock_resend = MagicMock()
    mock_resend.api_key = None
    mock_resend.Emails = MagicMock()
    mock_resend.Emails.send = MagicMock(return_value={"id": "test_id"})
    
    # 替换 sys.modules 中的 resend
    sys.modules['resend'] = mock_resend
    
    yield
    
    # 清理
    if 'resend' in sys.modules:
        del sys.modules['resend']


@pytest.fixture
def temp_data_dir():
    """创建临时数据目录用于测试"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_env_vars():
    """设置测试环境变量"""
    original_env = os.environ.copy()
    os.environ.update({
        "RESEND_API_KEY": "test_api_key",
        "SENDER_FROM_ADDRESS": "Test Server <test@example.com>",
        "RECIPIENT_EMAIL": "recipient@example.com",
        "SERVER_NAME": "Test Server",
        "OUTAGE_THRESHOLD": "180",
        "NETWORK_OUTAGE_THRESHOLD": "300",
        "INTERNAL_TARGETS": "192.168.1.1,192.168.0.1",
        "EXTERNAL_TARGETS": "114.114.114.114,223.5.5.5",
        "DNS_TARGET": "baidu.com"
    })
    yield
    # 恢复环境变量
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def heartbeat_files(temp_data_dir):
    """创建心跳文件用于测试"""
    file_a = os.path.join(temp_data_dir, "heartbeat_a.log")
    file_b = os.path.join(temp_data_dir, "heartbeat_b.log")
    return file_a, file_b


@pytest.fixture
def network_status_file(temp_data_dir):
    """创建网络状态文件用于测试"""
    return os.path.join(temp_data_dir, "network_status.log")


@pytest.fixture
def network_history_file(temp_data_dir):
    """创建网络历史文件用于测试"""
    return os.path.join(temp_data_dir, "network_history.log")


@pytest.fixture
def pending_notifications_file(temp_data_dir):
    """创建待发送通知文件用于测试"""
    return os.path.join(temp_data_dir, "pending_notifications.log")


def get_current_timestamp():
    """获取当前时间戳"""
    return int(time.time())


def get_timestamp_seconds_ago(seconds):
    """获取几秒前的时间戳"""
    return int(time.time()) - seconds