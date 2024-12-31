import requests


# 企业微信推送
def send_wechat_message(config, title, content):
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={config['corp_id']}&corpsecret={config['corp_secret']}"
    token_response = requests.get(token_url).json()
    access_token = token_response.get("access_token")
    if not access_token:
        print(f"企业微信获取 Token 失败: {token_response.get('errmsg')}")
        return False

    send_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
    payload = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": config["agent_id"],
        "text": {
            "content": f"{title}\n\n{content}"
        },
        "safe": 0
    }
    response = requests.post(send_url, json=payload)
    return response.status_code == 200 and response.json().get("errcode") == 0


# Server 酱推送
def send_server_chan_message(config, title, content):
    url = f"https://sctapi.ftqq.com/{config['send_key']}.send"
    payload = {"title": title, "desp": content}
    response = requests.post(url, data=payload)
    return response.status_code == 200 and response.json().get("code") == 0


# 钉钉机器人推送
def send_dingtalk_message(config, title, content):
    url = config['webhook']
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"{title}\n\n{content}"
        }
    }
    response = requests.post(url, json=payload)
    return response.status_code == 200 and response.json().get("errcode") == 0


# Telegram 机器人推送
def send_telegram_message(config, title, content):
    url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
    payload = {
        "chat_id": config["chat_id"],
        "text": f"{title}\n\n{content}"
    }
    response = requests.post(url, json=payload)
    return response.status_code == 200 and response.json().get("ok", False)


# 通用推送接口
def send_notification(channel_config, title, content):
    if channel_config['type'] == 'wechat':
        return send_wechat_message(channel_config, title, content)
    elif channel_config['type'] == 'server_chan':
        return send_server_chan_message(channel_config, title, content)
    elif channel_config['type'] == 'dingtalk':
        return send_dingtalk_message(channel_config, title, content)
    elif channel_config['type'] == 'telegram':
        return send_telegram_message(channel_config, title, content)
    else:
        print(f"未知推送通道类型: {channel_config['type']}")
        return False
