import requests
import hashlib
import argparse
from urllib.parse import urlparse



def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def normalize_url(url):
    if not is_valid_url(url):
        if "://" not in url:  # 如果URL没有scheme，则添加默认的http://
            url = "http://" + url
        elif url.startswith("//"):  # 针对可能开头只有双斜杠的情况
            url = "http:" + url
    if url.endswith("/"):  # 如果URL以斜杠结尾，则删除最后一个字符
        url = url[:-1]
    return url

# Create argument parser
parser = argparse.ArgumentParser(description='Calculate MD5 hash of a URL content')
parser.add_argument('-u', '--url', type=str, help='URL to fetch content from')

# Parse command line arguments
args = parser.parse_args()

# Get URL from command line arguments
url = args.url


def is_id_matched(response_text):
    md5_hash = hashlib.md5(response_text.encode('utf-8')).hexdigest()
    print(md5_hash)
    return md5_hash

# 指定URL
#url = "http://113.78.91.26:8000/favicon.ico"

# 获取URL内容
url = (normalize_url(url))
print(url)

response = requests.get(url,verify=False)

# 检查请求是否成功
if response.status_code == 200:
    # 获取响应内容
    #content = response.text
    response_text = response.content.decode('utf-8', 'ignore')
    # 计算MD5值
    md5_hash = is_id_matched(response_text)
    # 输出MD5值
    print("MD5:", md5_hash)
else:
    print("无法获取内容，状态码:", response.status_code)

