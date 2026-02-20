import re


def is_image_url(url):
    # 正则表达式，匹配以 https://multimedia.nt.qq.com.cn/download? 开头的链接
    pattern = r'^https://multimedia\.nt\.qq\.com\.cn/download\?'

    # 使用 re.match 来判断链接是否匹配
    if re.match(pattern, url):
        return True
    return False
