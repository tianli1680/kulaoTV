import requests
import re
import os

def download_m3u(url):
    """下载M3U文件"""
    try:
        print(f"正在从 {url} 下载文件...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
        
        # 使用session来保持连接
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # 尝试不同的编码
        content = response.text
        if not content:
            content = response.content.decode('utf-8', errors='ignore')
        
        print(f"下载成功，文件大小: {len(content)} 字节")
        print(f"文件开头: {content[:200]}")
        return content
    except Exception as e:
        print(f"下载失败: {e}")
        return None

def parse_m3u_simple(content):
    """简单的M3U解析方法"""
    channels = []
    
    # 定义排序顺序
    order = [
        '[联通]央卫视直播',
        '[电信]央卫视直播', 
        '[三网]央卫视直播',
        '[移动]央卫视直播'
    ]
    
    # 按行分割
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 查找EXTINF行
        if '#EXTINF:' in line:
            # 获取下一行作为URL
            if i + 1 < len(lines):
                url_line = lines[i + 1].strip()
                
                # 检查URL行是否有效（不以#开头）
                if url_line and not url_line.startswith('#'):
                    # 提取group-title
                    group_match = re.search(r'group-title="([^"]*)"', line)
                    if group_match:
                        group_title = group_match.group(1)
                        
                        # 检查是否在目标列表中
                        if any(keyword in group_title for keyword in ['联通', '电信', '三网', '移动']):
                            # 提取频道名称
                            name_match = re.search(r',(.+)$', line)
                            channel_name = name_match.group(1) if name_match else "未知频道"
                            
                            # 确定排序顺序
                            order_index = 999
                            for idx, g in enumerate(order):
                                if g in group_title:
                                    order_index = idx
                                    break
                            
                            channel = {
                                'info': line,
                                'url': url_line,
                                'group': group_title,
                                'name': channel_name,
                                'order': order_index
                            }
                            channels.append(channel)
                            print(f"找到频道: {channel_name} - {group_title}")
                    
                    i += 2
                    continue
        i += 1
    
    return channels

def parse_m3u_regex(content):
    """使用正则表达式解析M3U文件"""
    channels = []
    
    # 定义排序顺序
    order = [
        '[联通]央卫视直播',
        '[电信]央卫视直播', 
        '[三网]央卫视直播',
        '[移动]央卫视直播'
    ]
    
    # 正则表达式匹配EXTINF行和URL
    pattern = r'(#EXTINF:[^\n]+)\n([^\n]+)'
    matches = re.findall(pattern, content, re.MULTILINE)
    
    print(f"正则表达式找到 {len(matches)} 个匹配项")
    
    for info_line, url in matches:
        # 检查group-title
        if 'group-title="' in info_line:
            # 提取group-title
            group_match = re.search(r'group-title="([^"]*)"', info_line)
            if group_match:
                group_title = group_match.group(1)
                
                # 检查是否包含目标关键词
                if any(keyword in group_title for keyword in ['联通', '电信', '三网', '移动']):
                    # 提取频道名称
                    name_match = re.search(r',([^,]+)$', info_line)
                    channel_name = name_match.group(1) if name_match else "未知频道"
                    
                    # 确定排序顺序
                    order_index = 999
                    for idx, g in enumerate(order):
                        if g in group_title:
                            order_index = idx
                            break
                    
                    channel = {
                        'info': info_line.strip(),
                        'url': url.strip(),
                        'group': group_title,
                        'name': channel_name,
                        'order': order_index
                    }
                    channels.append(channel)
                    print(f"找到频道: {channel_name} - {group_title}")
    
    return channels

def write_m3u(channels, filename):
    """写入M3U文件"""
    try:
        print(f"\n正在写入文件: {filename}")
        
        # 按order排序
        channels.sort(key=lambda x: x['order'])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            
            for channel in channels:
                f.write(f"{channel['info']}\n")
                f.write(f"{channel['url']}\n")
        
        # 验证文件
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"文件创建成功: {filename}, 大小: {file_size} 字节")
            
            # 统计各组的频道数量
            groups = {}
            for ch in channels:
                groups[ch['group']] = groups.get(ch['group'], 0) + 1
            
            print("\n最终频道统计:")
            for group_name, count in groups.items():
                print(f"  {group_name}: {count} 个频道")
            
            return True
        else:
            print(f"警告: 文件 {filename} 未创建")
            return False
            
    except Exception as e:
        print(f"写入文件时出错: {e}")
        return False

def main():
    url = "https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1.m3u"
    output_file = "kulaoTV.m3u"
    
    print("=" * 60)
    print("开始处理M3U文件")
    print("=" * 60)
    
    # 下载文件
    content = download_m3u(url)
    
    if not content:
        print("下载失败，程序退出")
        return
    
    print("\n" + "=" * 60)
    print("尝试第一种解析方法（逐行解析）")
    print("=" * 60)
    channels1 = parse_m3u_simple(content)
    print(f"第一种方法找到 {len(channels1)} 个频道")
    
    print("\n" + "=" * 60)
    print("尝试第二种解析方法（正则表达式）")
    print("=" * 60)
    channels2 = parse_m3u_regex(content)
    print(f"第二种方法找到 {len(channels2)} 个频道")
    
    # 选择结果较多的方法
    if len(channels2) > len(channels1):
        channels = channels2
        method = "正则表达式方法"
    else:
        channels = channels1
        method = "逐行解析方法"
    
    print(f"\n选择使用 {method}，共找到 {len(channels)} 个频道")
    
    if channels:
        # 写入文件
        success = write_m3u(channels, output_file)
        
        if success:
            print(f"\n成功生成 {output_file}")
            
            # 按指定顺序显示统计
            order = ['[联通]央卫视直播', '[电信]央卫视直播', '[三网]央卫视直播', '[移动]央卫视直播']
            print("\n按指定顺序统计:")
            for group in order:
                count = sum(1 for ch in channels if group in ch['group'])
                print(f"  {group}: {count} 个频道")
    else:
        print("\n未找到符合条件的频道")
        # 创建一个示例文件用于测试
        print("创建示例文件用于测试...")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write('#EXTINF:-1 group-title="[联通]央卫视直播" tvg-id="1",CCTV-1\n')
            f.write('http://example.com/stream1\n')
            f.write('#EXTINF:-1 group-title="[电信]央卫视直播" tvg-id="2",CCTV-2\n')
            f.write('http://example.com/stream2\n')
        print(f"已创建示例文件: {output_file}")
    
    print("\n" + "=" * 60)
    print("处理完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
