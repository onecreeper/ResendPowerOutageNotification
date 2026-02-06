"""磁盘监控模块

提供磁盘空间监控功能
"""

import os
import shutil


def check_disk_space(path="/data", min_free_mb=100):
    """检查磁盘剩余空间
    
    Args:
        path: 要检查的路径
        min_free_mb: 最小剩余空间（MB）
        
    Returns:
        (has_enough_space, total_gb, used_gb, free_gb, free_mb): 
        是否有足够空间、总空间、已用空间、剩余空间（GB）、剩余空间（MB）
    """
    try:
        usage = shutil.disk_usage(path)
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        free_mb = usage.free / (1024**2)
        
        has_enough = free_mb >= min_free_mb
        
        return has_enough, total_gb, used_gb, free_gb, free_mb
    except Exception as e:
        print(f"检查磁盘空间失败: {e}")
        return False, 0, 0, 0, 0


def get_disk_usage_str(path="/data"):
    """获取磁盘使用情况的字符串描述
    
    Args:
        path: 要检查的路径
        
    Returns:
        str: 磁盘使用情况描述
    """
    try:
        usage = shutil.disk_usage(path)
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        percent = (usage.used / usage.total) * 100
        
        return f"{used_gb:.1f}GB / {total_gb:.1f}GB ({percent:.1f}%), 剩余 {free_gb:.1f}GB"
    except Exception as e:
        return f"无法获取磁盘使用情况: {e}"