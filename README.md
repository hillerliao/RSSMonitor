**项目简介**

RSS Monitor 是一个用于监控和管理 RSS 源的脚本。它可以检查 RSS 的新内容并推送到指定消息通道。

ChatGPT辅助生成的代码。

可以部署到青龙面板等。

**使用方法**

1. 安装依赖：`pip install -r requirements.txt`；
2. 配置 RSS 源：编辑 `config.json` 文件添加 RSS 源和对应消息通道；
3. 运行程序：`python rss_monitor.py`。

**配置文件**

配置文件 `config.json` 格式如下：
```json
{
  "rss_groups": [
    {
      "group_name": "新闻组",
      "rss_urls": [
        "https://news.example.com/rss1",
        "https://news.example.com/rss2"
      ],
      "push_channels": [
        {
          "type": "wecom",
          "corp_id": "wx123",
          "corp_secret": "secret123",
          "agent_id": "100001"
        },
        {
          "type": "server_chan",
          "send_key": "SCT123KEY"
        }
      ]
    }
  ]
}
```
**推送通道**

当前支持以下推送通道：

* 企业微信（wechat）
* Server 酱（server_chan）
* 钉钉机器人（dingtalk）
* Telegram 机器人（telegram）

**贡献**

欢迎贡献代码！请提交 Pull Request 或报告问题。

**许可证**

该项目基于 MIT 许可证，详细信息请参阅 [LICENSE](./LICENSE) 文件。