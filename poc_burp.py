import json

def parse_burp_request(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # 分离请求部分和返回匹配部分
    if "\n-\n" not in content:
        raise ValueError("文件格式错误，缺少 '-' 分隔符！")

    request_part, match_part = content.split("\n-\n", 1)
    match_pattern = match_part.strip()

    # 提取请求行 (HTTP 方法和 URL)
    request_lines = request_part.split("\n")
    request_line = request_lines[0]
    method, url, _ = request_line.split(" ", 2)

    # 提取头信息
    headers = {}
    body = ""
    header_end = False
    for line in request_lines[1:]:
        if line.strip() == "":  # 空行后开始正文数据
            header_end = True
            continue
        if not header_end:
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
        else:
            body += line + "\n"

    # 确保正文无多余引号
    body = body.strip()
    if body.startswith('"') and body.endswith('"'):
        body = body[1:-1]  # 去掉首尾的引号

    # 构造 JSON 格式的 PoC
    poc = {
        "name": "converted_poc",
        "method": method,
        "url": url,
        "headers": headers,
        "data": body,  # 保留原始正文格式
        "match": match_pattern
    }
    return poc

def save_poc_to_json(poc, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(poc, f, indent=4, ensure_ascii=False)
    print(f"PoC 已保存到 {output_file}")

def main():
    burp_file = "poc.txt"  # 输入 Burp 的请求文件路径
    output_file = "converted_poc.json"  # 输出的 JSON 文件路径

    try:
        poc = parse_burp_request(burp_file)
        save_poc_to_json(poc, output_file)
    except Exception as e:
        print(f"解析文件时出错: {e}")

if __name__ == "__main__":
    main()
