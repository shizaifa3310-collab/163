import requests
import base64
import os
import json
from datetime import datetime
from urllib.parse import quote

# ================= ⚙️ 核心配置区 ⚙️ =================

# 1. 自定义你的节点名称前缀
CUSTOM_REMARK = "科技共享节点分享"

# 2. 节点订阅源库（在此处随意添加新链接）
SOURCE_URLS = [
    "https://cdn.jsdelivr.net/gh/Pawdroid/Free-servers@main/sub",
    "https://cdn.jsdelivr.net/gh/mfuu/v2ray@master/v2ray",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v202605312",
    "https://raw.githubusercontent.com/chengaopan/AutoMergePublicNodes/master/list.txt",
    "https://github.cmliussss.net/https://raw.githubusercontent.com/qmqv/jd07/refs/heads/main/v207-1010.txt",
    "https://ghfast.top/https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt",
    "https://proxy.v2gh.com/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://gt.1155555.xyz/https://raw.githubusercontent.com/shaoyouvip/free/refs/heads/main/base64.txt",
    "",
    "",
    "",
    # ⬇️ 以后有新链接，按下面这种格式加在后面即可（注意双引号和逗号）：
    # "https://你的新订阅链接.com/sub",
]

# 3. 垃圾节点过滤黑名单（可自行添加别人节点里的广告词过滤掉）
BLACKLIST_KEYWORDS = ['-1', '127.0.0.1', 'timeout', 'err', '错误', '剩余', '到期', '官网', 'mibei77']

# ====================================================

SUPPORTED_PROTOCOLS = ('vmess://', 'vless://', 'ss://', 'ssr://', 'trojan://', 'tuic://', 'hysteria2://')

def fetch_and_decode(url):
    try:
        print(f"[*] 正在抓取: {url}")
        # 伪装请求头，防止被部分源站拦截
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        content = response.text.strip()
        
        try:
            padding = 4 - (len(content) % 4)
            if padding != 4: content += "=" * padding
            decoded_bytes = base64.b64decode(content)
            return decoded_bytes.decode('utf-8', errors='ignore').splitlines()
        except:
            return content.splitlines()
    except Exception as e:
        print(f"[!] 抓取失败 {url}: {e}")
        return []

def rename_node(link, index):
    """智能节点重命名核心逻辑"""
    # 生成带编号的新名字，例如：科技共享节点分享 001
    new_name = f"{CUSTOM_REMARK} {index:03d}"
    
    if link.startswith("vmess://"):
        try:
            # 剥离前缀
            b64_str = link[8:]
            # 修复 Base64 长度补全
            padding = 4 - (len(b64_str) % 4)
            if padding != 4: b64_str += "=" * padding
            
            # 解码为 JSON
            v_json = json.loads(base64.b64decode(b64_str).decode('utf-8'))
            # 修改节点别名字段
            v_json['ps'] = new_name
            
            # 重新打包为 Base64
            new_b64 = base64.b64encode(json.dumps(v_json, ensure_ascii=False).encode('utf-8')).decode('utf-8')
            return f"vmess://{new_b64}"
        except Exception:
            return link # 解析失败则保留原样
            
    elif any(link.startswith(p) for p in ['vless://', 'trojan://', 'ss://', 'ssr://']):
        try:
            # 提取 # 之前的节点主体部分
            base_link = link.split("#", 1)[0]
            # 拼接新的 URL 编码后的名称
            return f"{base_link}#{quote(new_name)}"
        except Exception:
            return link
            
    return link

def main():
    print(f"=== 开始执行高级抓取与清洗任务 {datetime.now()} ===")
    all_lines = []
    
    for url in SOURCE_URLS:
        all_lines.extend(fetch_and_decode(url))
        
    valid_nodes = []
    
    for line in all_lines:
        line = line.strip()
        if not line.startswith(SUPPORTED_PROTOCOLS):
            continue
            
        # 黑名单过滤过滤
        is_bad = any(keyword.lower() in line.lower() for keyword in BLACKLIST_KEYWORDS)
        if is_bad:
            continue
            
        valid_nodes.append(line)
        
    # 初步去重
    valid_nodes = list(set(valid_nodes))
    
    print(f"[*] 清洗完毕，正在进行全自动重命名...")
    
    final_nodes = []
    # 遍历节点并执行重命名，传入编号 i
    for i, node in enumerate(valid_nodes, 1):
        renamed_node = rename_node(node, i)
        final_nodes.append(renamed_node)
        
    print(f"[*] 成功生成 {len(final_nodes)} 个定制化节点！")
    
    # 将节点拼接成文本并 Base64 编码
    raw_text = "\n".join(final_nodes)
    sub_base64 = base64.b64encode(raw_text.encode('utf-8')).decode('utf-8')
    
    os.makedirs('output', exist_ok=True)
    with open('output/nodes.txt', 'w', encoding='utf-8') as f:
        f.write(raw_text)
    with open('output/sub.txt', 'w', encoding='utf-8') as f:
        f.write(sub_base64)

if __name__ == "__main__":
    main()
