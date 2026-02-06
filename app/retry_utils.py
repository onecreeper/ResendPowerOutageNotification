"""重试工具模块

提供带指数退避的重试机制
"""

import time


def retry_with_backoff(func, max_retries=3, initial_delay=1, backoff_factor=2, 
                       exceptions=(Exception,), should_retry_func=None):
    """带指数退避的重试函数
    
    Args:
        func: 要重试的函数
        max_retries: 最大重试次数（默认3次）
        initial_delay: 初始延迟秒数（默认1秒）
        backoff_factor: 退避因子（每次重试延迟乘以这个值，默认2）
        exceptions: 需要重试的异常类型（默认所有异常）
        should_retry_func: 判断是否应该重试的函数，返回True则重试
        
    Returns:
        函数执行结果
        
    Raises:
        最后一次异常（如果所有重试都失败）
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            
            # 如果是最后一次尝试，不再重试
            if attempt >= max_retries:
                raise
            
            # 如果提供了should_retry_func且返回False，不再重试
            if should_retry_func and not should_retry_func(e, attempt):
                raise
            
            # 打印重试信息
            print(f"邮件发送失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
            print(f"等待 {delay:.1f} 秒后重试...")
            
            # 等待一段时间后重试
            time.sleep(delay)
            delay *= backoff_factor  # 指数退避
    
    # 如果所有重试都失败，抛出最后一个异常
    if last_exception:
        raise last_exception


def is_retryable_error(exception, attempt):
    """判断错误是否可以重试
    
    Args:
        exception: 异常对象
        attempt: 当前尝试次数（从0开始）
        
    Returns:
        bool: 如果应该重试返回True
    """
    # 某些错误不应该重试（如认证失败）
    error_str = str(exception).lower()
    
    # 认证相关错误不重试
    if 'authentication' in error_str or 'unauthorized' in error_str or 'invalid api key' in error_str:
        return False
    
    # 速率限制应该重试
    if 'rate limit' in error_str or '429' in error_str:
        return True
    
    # 网络错误应该重试
    if 'connection' in error_str or 'timeout' in error_str or 'network' in error_str:
        return True
    
    # 服务器错误（5xx）应该重试
    if any(code in error_str for code in ['500', '502', '503', '504']):
        return True
    
    # 默认重试
    return True