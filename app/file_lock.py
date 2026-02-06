"""
文件锁工具模块
使用 fcntl (Linux/Mac) 或 msvcrt (Windows) 实现跨平台文件锁
"""

import os
import sys
import time
from contextlib import contextmanager
from typing import Optional

# 从环境变量读取是否启用文件锁（测试环境可能需要禁用）
ENABLE_FILE_LOCK = os.getenv('ENABLE_FILE_LOCK', 'true').lower() == 'true'


class FileLock:
    """跨平台文件锁实现"""
    
    def __init__(self, filepath: str, timeout: float = 10.0):
        """
        初始化文件锁
        
        Args:
            filepath: 要锁定的文件路径
            timeout: 获取锁的超时时间（秒）
        """
        self.filepath = filepath
        self.timeout = timeout
        self.lock_file = f"{filepath}.lock"
        self.fd: Optional[int] = None
        
    def acquire(self) -> bool:
        """
        获取文件锁
        
        Returns:
            bool: 是否成功获取锁
        """
        if self.fd is not None:
            return True  # 已经持有锁
        
        # 确保锁文件目录存在
        lock_dir = os.path.dirname(self.lock_file)
        if lock_dir and not os.path.exists(lock_dir):
            try:
                os.makedirs(lock_dir, exist_ok=True)
            except OSError:
                pass  # 如果目录创建失败，继续尝试（可能是权限问题）
            
        start_time = time.time()
        
        while True:
            try:
                # 以读写模式打开锁文件
                self.fd = os.open(self.lock_file, os.O_CREAT | os.O_WRONLY, 0o644)
                
                # 根据平台选择锁定方式
                if sys.platform == 'win32':
                    import msvcrt
                    msvcrt.locking(self.fd, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                
                # 写入当前进程ID
                os.write(self.fd, str(os.getpid()).encode())
                return True
                
            except (IOError, OSError, BlockingIOError):
                # 锁定失败，关闭文件句柄
                if self.fd is not None:
                    os.close(self.fd)
                    self.fd = None
                
                # 检查是否超时
                if time.time() - start_time >= self.timeout:
                    return False
                
                # 等待一小段时间后重试
                time.sleep(0.1)
    
    def release(self) -> None:
        """释放文件锁"""
        if self.fd is None:
            return
        
        try:
            # 根据平台选择解锁方式
            if sys.platform == 'win32':
                import msvcrt
                msvcrt.locking(self.fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.fd, fcntl.LOCK_UN)
        finally:
            # 关闭文件句柄
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
            
            # 删除锁文件
            try:
                os.unlink(self.lock_file)
            except OSError:
                pass
    
    def __enter__(self):
        """支持 with 语句"""
        if not self.acquire():
            raise TimeoutError(f"无法在 {self.timeout} 秒内获取文件锁: {self.filepath}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出 with 语句时释放锁"""
        self.release()
        return False


@contextmanager
def file_lock(filepath: str, timeout: float = 10.0):
    """
    文件锁上下文管理器
    
    Args:
        filepath: 要锁定的文件路径
        timeout: 获取锁的超时时间（秒）
    
    Example:
        with file_lock('/data/heartbeat_a.log'):
            # 安全地读写文件
            with open('/data/heartbeat_a.log', 'w') as f:
                f.write(data)
    """
    if not ENABLE_FILE_LOCK:
        # 如果文件锁被禁用，什么都不做
        yield None
        return
    
    lock = FileLock(filepath, timeout)
    lock.acquire()
    try:
        yield lock
    finally:
        lock.release()