import json
import hashlib
import time
from datetime import datetime
import os
import feedparser
from html.parser import HTMLParser
from urllib.parse import quote
from push_service import send_notification

# HTML 清理工具
class HTMLCleaner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def get_data(self):
        return ''.join(self.fed)


def clean_html(html):
    cleaner = HTMLCleaner()
    cleaner.feed(html)
    return cleaner.get_data()


# 加载配置文件
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


# 获取当前年月作为文件名，并保存在 `rssJsonFiles` 文件夹内
def get_file_name():
    now = datetime.now()
    folder_path = 'rssJsonFiles'
    os.makedirs(folder_path, exist_ok=True)  # 确保文件夹存在
    return os.path.join(folder_path, f"seen_hashes_{now.year}_{now.month}.json")

# 加载已处理的哈希值及文章信息
def load_seen_hashes():
    file_name = get_file_name()
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # 如果文件不存在，则创建一个空的 JSON 文件
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []

# 保存已处理的哈希值及文章信息
def save_seen_hashes(seen_hashes):
    file_name = get_file_name()
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(seen_hashes, f, ensure_ascii=False, indent=4)


# 检查 RSS 分组
def check_rss_group(rss_group, seen_hashes):
    group_name = rss_group['group_name']
    rss_urls = rss_group['rss_urls']
    push_channels = rss_group['push_channels']  # 支持多个推送通道

    print(f"检查 RSS 分组: {group_name}")

    for rss_url in rss_urls:
        # 对 RSS 地址进行 URL 编码
        encoded_url = quote(rss_url, safe=':/?=&')
        print(f"访问 RSS 地址: {encoded_url}")

        feed = feedparser.parse(encoded_url)
        feed_title = feed.feed.title if 'title' in feed.feed else 'RSS更新提醒'

        for entry in feed.entries:
            entry_hash = hashlib.md5(entry.link.encode('utf-8')).hexdigest()

            if not any(item['hash'] == entry_hash for item in seen_hashes):
                title = entry.title
                link = entry.link  # 获取条目的 URL
                summary = clean_html(entry.summary) if 'summary' in entry and clean_html(entry.summary) != title else "无摘要" if 'summary' not in entry else ""
 
                content = {"feed_title": feed_title, "title": title, "link": link, "summary": summary}

                # 推送到多个通道
                for channel in push_channels:
                    success = send_notification(channel, content)
                    if success:
                        print(f"推送成功: [{channel['type']}] {title}")
                    else:
                        print(f"推送失败: [{channel['type']}] {title}")

                    # 消息间隔 2 秒
                    time.sleep(2)

                # 记录已处理文章
                seen_hashes.append({
                    'hash': entry_hash,
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'group': group_name,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

                # 保存已处理的哈希记录
                save_seen_hashes(seen_hashes)


# 主程序
def main():
    config = load_config()
    seen_hashes = load_seen_hashes()  # 加载已处理的哈希记录

    for rss_group in config['rss_groups']:
        check_rss_group(rss_group, seen_hashes)

    # 最后保存所有已处理的哈希记录
    save_seen_hashes(seen_hashes)


if __name__ == "__main__":
    main()
