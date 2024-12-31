import json
import hashlib
import time
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

            if entry_hash not in seen_hashes:
                title = entry.title
                link = entry.link  # 获取条目的 URL
                summary = clean_html(entry.summary) if 'summary' in entry else "无摘要"

                # 拼接消息内容
                content = f"标题: {title}\n链接: {link}\n摘要: {summary}"

                # 推送到多个通道
                for channel in push_channels:
                    success = send_notification(channel, feed_title, content)
                    if success:
                        print(f"推送成功: [{channel['type']}] {title}")
                    else:
                        print(f"推送失败: [{channel['type']}] {title}")

                    # 消息间隔 2 秒
                    time.sleep(2)

                # 记录已处理文章
                seen_hashes.add(entry_hash)


# 主程序
def main():
    config = load_config()
    seen_hashes = set()

    for rss_group in config['rss_groups']:
        check_rss_group(rss_group, seen_hashes)


if __name__ == "__main__":
    main()