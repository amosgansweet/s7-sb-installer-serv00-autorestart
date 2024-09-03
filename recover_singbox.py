
import os
import json
import subprocess
import requests

def send_telegram_message(token, chat_id, message):
    telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
    telegram_payload = {
        "chat_id": chat_id,
        "text": message,
        "reply_markup": '{"inline_keyboard":[[{"text":"问题反馈❓","url":"https://t.me/amosgantian"}]]}'
    }

    response = requests.post(telegram_url, json=telegram_payload)
    print(f"Telegram 请求状态码：{response.status_code}")
    print(f"Telegram 请求返回内容：{response.text}")

    if response.status_code != 200:
        print("发送 Telegram 消息失败")
    else:
        print("发送 Telegram 消息成功")

# 从环境变量中获取密钥
accounts_json = os.getenv('ACCOUNTS_JSON')
telegram_token = os.getenv('TELEGRAM_TOKEN')
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

# 检查并解析 JSON 字符串
try:
    servers = json.loads(accounts_json)
except json.JSONDecodeError:
    error_message = "ACCOUNTS_JSON 参数格式错误"
    print(error_message)
    send_telegram_message(telegram_token, telegram_chat_id, error_message)
    exit(1)

# 初始化汇总消息
summary_message = "serv00-vless 恢复操作结果：\n"

# 默认恢复命令
default_restore_commands = ["ps aux | grep -v grep | grep sing-box > /dev/null || nohup $HOME/sing-box/sing-box run -c $HOME/sing-box/data/config.json > $HOME/sing-box/data/sing-box.log 2>&1 &",
                           "ps aux | grep -v grep | grep server > /dev/null || nohup $HOME/hysteria/S7-Hysteria-install-serv00.sh >/dev/null  2>&1 &",
                           "ps aux | grep -v grep | grep nezha-agent > /dev/null || nohup $HOME/nezha-agent/nezha-agent.sh >/dev/null  2>&1 &"
                          ]

# 遍历服务器列表并执行恢复操作
for server in servers:
    host = server['host']
    port = server['port']
    username = server['username']
    password = server['password']
    cron_command = server.get('cron', default_restore_command)

    print(f"连接到 {host}...")

    # 执行恢复命令（这里假设使用 SSH 连接和密码认证）
    for command in cron_commands:
        restore_command = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -p {port} {username}@{host} '{command}'"
        print(f"执行命令: {restore_command}")  # 添加日志
        try:
            output = subprocess.check_output(restore_command, shell=True, stderr=subprocess.STDOUT)
            summary_message += f"\n成功恢复 {host} 上的 singbox and nezha 服务：\n{output.decode('utf-8')}"
        except subprocess.CalledProcessError as e:
            error_output = e.output.decode('utf-8')
            print(f"执行命令失败: {restore_command}\n错误信息: {error_output}")  # 添加日志
            summary_message += f"\n未能恢复 {host} 上的 singbox and nezha 服务：\n{error_output}"
        except Exception as e:
            error_message = str(e)
            print(f"未知错误: {error_message}")  # 捕获其他异常
            summary_message += f"\n未能恢复 {host} 上的 singbox and nezha 服务：\n{error_message}"

# 发送汇总消息到 Telegram
send_telegram_message(telegram_token, telegram_chat_id, summary_message)
