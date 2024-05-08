import json
import requests
import re
import threading
import argparse
import hashlib
from urllib.parse import urlparse
from requests.exceptions import Timeout
from tqdm import tqdm
import time
import concurrent.futures



# 设置用户代理和请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'Proxy-Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6'
}

# 定义全局事件
request_event = threading.Event()

def normalize_url(url):
    if not is_valid_url(url):
        if "://" not in url:
            url = "http://" + url
        elif url.startswith("//"):
            url = "http:" + url
    if url.endswith("/"):
        url = url[:-1]
    return url

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def is_id_matched(id_value, response_text):
    if isinstance(id_value, dict) and "regex" in id_value:
        regex_pattern = id_value["regex"]
        return bool(re.search(regex_pattern, response_text))
    elif "MD5" in id_value:
        md5_hash = hashlib.md5(response_text.encode('utf-8')).hexdigest()
        return md5_hash == id_value["MD5"]
    elif "_header" in id_value:
        id_value = id_value["_header"]
        return id_value in response_text
    elif isinstance(id_value, str):
        return id_value in response_text
    return False

def process_url_thread(url, data, output_file):
    id_value = data.get("id")
    name_value = data.get("name")
    path_value = data.get("path", "")

    url = normalize_url(url)

    if path_value:
        _url = url.rstrip('/') +  path_value

    if not is_valid_url(url):
        print("Invalid URL:", url)
        return
    try:
        response = requests.get(_url, timeout=5, verify=False, headers=headers)
        response_text = response.content.decode('utf-8', 'ignore')

        if is_id_matched(id_value, response_text):
            result = url +"\t"+ name_value
            print(result)
            output_file.write(result + '\n')
        elif is_id_matched(id_value, str(response.headers)):
            result = url +"\t"+ name_value
            print(result)
            output_file.write(result + '\n')
    except Timeout:
        print(f"Timeout occurred for URL: {url}. Skipping...")
    except Exception as e:
        #print(str(e))
        pass
    finally:
        # 等待一段时间后再执行下一个请求
        time.sleep(args.delay)


def process_url_file(filename, json_filename, output_filename, num_threads):
    # 读取 URL 文件和 JSON 文件
    with open(filename, 'r', encoding='utf-8') as url_file:
        urls = url_file.readlines()
    with open(json_filename, 'r', encoding='utf-8') as json_file:
        json_data = [json.loads(line) for line in json_file]

    # 计算总迭代次数
    total_iterations = len(urls) * len(json_data)

    # 打开输出文件
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        # 使用 ThreadPoolExecutor 管理线程池，并限制同时运行的线程数量为 num_threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            # 遍历 JSON 数据和 URL 列表，为每个组合提交一个任务
            for data in json_data:
                for url in urls:
                    # 提交任务给线程池执行，并将返回的 Future 对象保存在 futures 列表中
                    future = executor.submit(process_url_thread, url.strip(), data, output_file)
                    futures.append(future)

            # 显示进度条，跟踪处理的 URL 数量
            progress_bar = tqdm(total=total_iterations, desc="Processing URLs", unit="URL")
            # 遍历所有 Future 对象，等待任务完成
            for future in concurrent.futures.as_completed(futures):
                progress_bar.update(1)  # 更新进度条
            progress_bar.close()  # 关闭进度条



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--threads", type=int, default=6, help="Number of threads default 6")
    parser.add_argument("-f", "--file", type=str, default='1.txt',help="file e.g -f 1.txt")
    parser.add_argument("-delay", "--delay", type=int, default=0, help="Delay time in seconds between requests")
    args = parser.parse_args()

    url_filename = args.file
    json_filename = "finger.json"
    output_filename = "output.txt"

    # 设置事件使得线程之间有一定的延迟
    request_event.set()

    process_url_file(url_filename, json_filename, output_filename, num_threads=args.threads)
