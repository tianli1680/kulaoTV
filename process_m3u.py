import requests
import re
from collections import OrderedDict

def download_m3u(url):
    """下载M3U文件"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"下载失败: {e}")
        return None

def parse_m3u(content):
    """解析M3U内容，按group-title分类"""
    lines = content.strip().split('\n')
    channels = []
    current_channel = None
    
    # 定义排序顺序
    order = [
        '[联通]央卫视直播',
        '[电信]央卫视直播', 
        '[三网]央卫视直播',
        '[移动]央卫视直播'
    ]
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 跳过空行
        if not line:
            i += 1
            continue
        
        # 处理EXTINF行
        if line.startswith('#EXTINF:'):
            channel_info = line
            # 检查下一行是否是URL
            if i + 1 < len(lines) and not lines[i + 1].startswith('#'):
                url = lines[i + 1].strip()
                
                # 提取group-title
                group_match = re.search(r'group-title="([^"]+)"', channel_info)
                if group_match:
                    group_title = group_match.group(1)
                    
                    # 只保留指定顺序的频道
                    if group_title in order:
                        channels.append({
                            'info': channel_info,
                            'url': url,
                            'group': group_title,
                            'order': order.index(group_title)
                        })
                
                i += 2  # 跳过已处理的两行
            else:
                i += 1
        else:
            i += 1
    
    return channels

def sort_channels(channels):
    """按指定顺序排序频道"""
    # 先按group排序，保持原有顺序
    channels.sort(key=lambda x: x['order'])
    return channels

def write_m3u(channels, filename):
    """写入M3U文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        
        for channel in channels:
            f.write(f"{channel['info']}\n")
            f.write(f"{channel['url']}\n")

def main():
    url = "https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1.m3u"
    output_file = "kulaoTV.m3u"
    
    print("正在下载M3U文件...")
    content = download_m3u(url)
    
    if content:
        print("正在解析频道...")
        channels = parse_m3u(content)
        
        print(f"找到 {len(channels)} 个符合条件的频道")
        
        if channels:
            print("正在排序频道...")
            channels = sort_channels(channels)
            
            print("正在写入文件...")
            write_m3u(channels, output_file)
            
            print(f"成功生成 {output_file}")
            
            # 显示分组统计
            groups = {}
            for ch in channels:
                groups[ch['group']] = groups.get(ch['group'], 0) + 1
            
            print("\n频道统计:")
            for group in ['[联通]央卫视直播', '[电信]央卫视直播', '[三网]央卫视直播', '[移动]央卫视直播']:
                if group in groups:
                    print(f"  {group}: {groups[group]} 个频道")
        else:
            print("未找到符合条件的频道")
            # 创建一个空文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('#EXTM3U\n')
    else:
        print("下载失败，使用现有文件（如果有）")

if __name__ == "__main__":
    main()
