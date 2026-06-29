#!/usr/bin/env python3
"""Fix Telegram bot - test and configure."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

# Test Telegram bot directly on server
commands = """
cd /var/www/englishpro
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
import telegram
import asyncio

async def test():
    token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    print(f'BOT_TOKEN: {token[:10]}...{token[-5:]}')
    print(f'CHAT_ID: {chat_id}')
    
    bot = telegram.Bot(token=token)
    
    # Try to get updates
    try:
        updates = await bot.get_updates()
        print(f'Updates count: {len(updates)}')
        for u in updates:
            if u.message:
                print(f'  Chat ID: {u.message.chat.id}, Type: {u.message.chat.type}, From: {u.message.from_user.id}')
    except Exception as e:
        print(f'Error getting updates: {e}')
    
    # Try to send message
    try:
        await bot.send_message(
            chat_id=int(chat_id),
            text='<b>✅ Тестовое сообщение!</b>\\n\\nБот настроен и работает!',
            parse_mode='HTML'
        )
        print('Message sent successfully!')
    except Exception as e:
        print(f'Error sending message: {e}')

asyncio.run(test())
"
"""

stdin, stdout, stderr = client.exec_command(commands)
print("=== Telegram Test ===")
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
