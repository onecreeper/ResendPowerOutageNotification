"""HTML工具模块

提供HTML转义和安全处理功能
"""

import html


def escape_html(text):
    """转义HTML特殊字符
    
    Args:
        text: 要转义的文本
        
    Returns:
        str: 转义后的文本
    """
    if text is None:
        return ""
    return html.escape(str(text))


def safe_format_email_content(template, **kwargs):
    """安全地格式化邮件内容，自动转义变量
    
    Args:
        template: 模板字符串（支持 {variable} 占位符）
        **kwargs: 要插入的变量
        
    Returns:
        str: 格式化并转义后的内容
    """
    # 转义所有变量值
    safe_kwargs = {k: escape_html(v) for k, v in kwargs.items()}
    
    # 格式化模板
    return template.format(**safe_kwargs)


def validate_html_content(content, allowed_tags=['html', 'body', 'h3', 'p', 'table', 'tr', 'td', 'strong']):
    """验证HTML内容，只允许特定标签
    
    Args:
        content: HTML内容
        allowed_tags: 允许的标签列表
        
    Returns:
        (is_valid, error_msg): 是否有效和错误信息
    """
    import re
    
    # 简单的标签白名单检查
    tag_pattern = r'<([a-zA-Z][a-zA-Z0-9]*)'
    found_tags = re.findall(tag_pattern, content)
    
    for tag in found_tags:
        if tag not in allowed_tags:
            return False, f"不允许的HTML标签: <{tag}>"
    
    # 检查可能的脚本注入
    if '<script' in content.lower() or 'javascript:' in content.lower():
        return False, "检测到潜在的脚本注入"
    
    return True, None