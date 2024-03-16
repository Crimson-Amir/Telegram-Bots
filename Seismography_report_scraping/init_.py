import os

list_of_commands = [
    "sudo apt update",
    "sudo apt install python3 python3-pip",
    "pip install -r requirement.txt",
    "systemctl daemon-reload",
    "systemctl start telegram_bot"
]

text = """
[Unit]
Description=My telegram bot
After=multi-user.target
[Service]
Type=simple
Restart=always
ExecStart=/root/venv/bin/python3 /root/main.py
[Install]
WantedBy=multi-user.target
"""

with open('/etc/systemd/system/telegram_bot.service', 'w') as e:
    e.write(text)

for command in list_of_commands:
    os.system(command)
