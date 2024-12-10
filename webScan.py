import json
import os
import threading
import requests
import re
import argparse
from queue import Queue
from colorama import init, Fore

# 初始化 colorama
init(autoreset=True)

# 加载配置文件
def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# 加载 PoC 文件
def load_poc(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# 检查配置合法性
def validate_config(config):
    if config['http_proxy']['enabled'] and config['cookie5_proxy']['enabled']:
        raise ValueError("HTTP代理和Cookie5代理不能同时启用！")

# 保存匹配成功的 URL
def save_successful_url(url, poc_file_name, file_path="yes.txt"):
    with open(file_path, "a") as f:
        f.write(f"{url}   PoC:{poc_file_name}\n")

# 扫描任务
def scan_task(target, poc, poc_file_name, proxies=None):
    try:
        # 拼接完整的 URL
        url = f"{target.rstrip('/')}{poc.get('url', '')}"
        method = poc.get("method", "GET").upper()
        headers = poc.get("headers", {})
        data = poc.get("data", "")
        match_pattern = poc.get("match", "")

        # 去除 data 字段中的多余引号
        if isinstance(data, str) and data.startswith('"') and data.endswith('"'):
            data = data[1:-1]  # 去掉首尾的引号

        # 根据方法发送请求
        if method == "GET":
            response = requests.get(url, headers=headers, proxies=proxies, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=5)
        elif method == "PUT":
            response = requests.put(url, headers=headers, data=data, proxies=proxies, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, proxies=proxies, timeout=5)
        else:
            return

        # 匹配返回包
        if match_pattern and re.search(match_pattern, response.text):
            print(Fore.RED + f"存在: {url}   PoC:{poc_file_name}")  # 匹配成功
            save_successful_url(url, poc_file_name)  # 保存成功的 URL
        else:
            print(f"不存在: {url}   PoC:{poc_file_name}")  # 匹配失败
    except Exception as e:
        return

# 多线程扫描器
class Scanner:
    def __init__(self, targets, config, poc_files):
        self.targets = targets
        self.config = config
        self.poc_files = poc_files
        self.queue = Queue()
        self.threads = []
        self.proxies = self.get_proxies()

    def get_proxies(self):
        proxies = {}
        if self.config['http_proxy']['enabled']:
            proxies = {
                "http": f"http://{self.config['http_proxy']['address']}",
                "https": f"http://{self.config['http_proxy']['address']}"
            }
        elif self.config['cookie5_proxy']['enabled']:
            proxies = {
                "http": f"http://{self.config['cookie5_proxy']['address']}",
                "https": f"http://{self.config['cookie5_proxy']['address']}"
            }
        return proxies

    def worker(self):
        while not self.queue.empty():
            target, poc, poc_file_name = self.queue.get()
            scan_task(target, poc, poc_file_name, self.proxies)
            self.queue.task_done()

    def run(self, thread_count=10):
        for target in self.targets:
            for poc_file in self.poc_files:
                poc = load_poc(poc_file)
                poc_file_name = os.path.basename(poc_file).rsplit('.', 1)[0]  # 去掉 .json 后缀
                self.queue.put((target, poc, poc_file_name))

        for _ in range(thread_count):
            t = threading.Thread(target=self.worker)
            t.start()
            self.threads.append(t)

        for t in self.threads:
            t.join()

# 主函数
def main():
    parser = argparse.ArgumentParser(description="PoC Scanning Tool")
    parser.add_argument("-u", help="单独扫描一个URL", metavar="URL")
    parser.add_argument("--info", help="显示帮助信息", action="store_true")
    parser.add_argument("-r", help="从文件导入URL列表", metavar="FILE")
    parser.add_argument("-o", help="指定PoC文件或全部扫描 (如: -o * 或 -o 2.json)", metavar="POC")

    args = parser.parse_args()

    # 显示帮助信息
    if args.info:
        parser.print_help()
        return

    # 加载配置
    config_file = "main.json"
    config = load_config(config_file)
    try:
        validate_config(config)
    except ValueError as e:
        print(e)
        return

    targets = []
    poc_files = []

    # 处理 -u 参数
    if args.u:
        targets.append(args.u)

    # 处理 -r 参数
    if args.r:
        with open(args.r, "r") as f:
            targets.extend([line.strip() for line in f if line.strip()])

    # 处理 -o 参数
    poc_directory = "root"
    if args.o == "*":
        poc_files = [os.path.join(poc_directory, f) for f in os.listdir(poc_directory) if f.endswith(".json")]
    elif args.o:
        poc_files = [os.path.join(poc_directory, args.o)]

    if not targets:
        print("未指定扫描目标，请使用 -u 或 -r 指定目标！")
        return

    if not poc_files:
        print("未指定PoC文件，请使用 -o 指定PoC文件或使用 -o * 扫描全部！")
        return

    # 初始化扫描器并运行
    scanner = Scanner(targets, config, poc_files)
    scanner.run(thread_count=5)

if __name__ == "__main__":
    main()
