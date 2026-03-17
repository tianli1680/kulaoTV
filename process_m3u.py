import re
import requests

# 配置
source_url = "https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1.m3u"
output_file = "kulaoTV.m3u"

# 定义排序优先级
priority = ["[联通]央卫视直播", "[电信]央卫视直播", "[三网]央卫视直播", "[移动]央卫视直播"]

def process_m3u():
    print(f"正在从 {source_url} 下载...")
    try:
        response = requests.get(source_url, timeout=10)
        response.encoding = 'utf-8'
        lines = response.text.splitlines()
    except Exception as e:
        print(f"下载失败: {e}")
        return

    # 解析频道
    channels = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            if i + 1 < len(lines):
                info_line = line
                url_line = lines[i + 1].strip()
                # 提取 group-title
                match = re.search(r'group-title="([^"]*)"', info_line)
                group = match.group(1) if match else ''
                channels.append({
                    'info': info_line,
                    'url': url_line,
                    'group': group
                })
                i += 2
            else:
                i += 1
        else:
            i += 1

    print(f"共解析到 {len(channels)} 个频道")

    # 按优先级排序
    def sort_key(channel):
        group = channel['group']
        return priority.index(group) if group in priority else len(priority)

    channels.sort(key=sort_key)

    # 写入新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for ch in channels:
            f.write(ch['info'] + '\n')
            f.write(ch['url'] + '\n')

    print(f"已完成排序并保存到 {output_file}")

if __name__ == "__main__":
    process_m3u()
