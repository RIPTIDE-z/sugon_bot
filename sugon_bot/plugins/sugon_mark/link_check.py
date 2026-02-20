# 导入requests库，用于发送请求
import imghdr

import requests


# 定义一个函数，用于检测文本是否是链接
def is_link(text):
    """暂无使用，用于检测是否为一个链接"""
    # 判断文本是否以http://或https://开头
    if text.startswith("http://") or text.startswith("https://"):
        return True
    else:
        return False


# 定义一个函数，用于检测链接是否可以访问
def is_accessible(link):
    """暂无使用，检测一个链接是否可达"""
    # 尝试发送请求到链接，并获取响应
    try:
        response = requests.get(link)
        # 判断响应的状态码是否是200，表示成功
        if response.status_code == 200:
            return True
        else:
            return False
    # 如果发送请求失败，说明链接不可访问
    except:

        return False


def is_image_url(url):
    """检测一个链接是否为图片"""
    # 尝试发送请求到链接，并获取响应的内容
    try:
        response = requests.get(url)
        content = response.content
        # 使用imghdr模块，通过读取文件头字节流判断图片类型
        image_type = imghdr.what(None, content)
        # 如果返回None，说明不是图片，否则返回图片类型
        if image_type is None:
            return False
        else:
            return image_type
    # 如果发送请求失败，说明链接不可访问
    except:
        return False
