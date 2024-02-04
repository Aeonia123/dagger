#!/usr/bin/env python3
import sys
import asyncio
from telegram import Bot

# This can be used to test the telegram bot setup. 
# Add your bot's token, add the bot to a chat,
# and add the chat id. Then run this script with a message
# and see if you get it in your chat.

# Example: talk_as_bot.py "hello world!"

# To get the chat id:
# 1. Add the bot to your chat
# 2a. Go here: https://api.telegram.org/bot<your_bot_token>/getUpdates
# OR
# 2b. run get_chat_token.py in this repo which does the same check
# 3. If all you see is {"ok":true,"result":[]}, or the script can't get the token, 
# remove and re-add the bot from your chat and try again


BOT_TOKEN = 'your_bot_token'
CHAT_ID = 'your_chat_id'

if len(sys.argv) != 2:
    print("Usage: talk_as_bot.py <message>")
    sys.exit(1)

user_input = sys.argv[1]

async def send_telegram_message(message):
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        log_error(f"Failed to send Telegram message: {e}")
        # Implement retry logic if needed

asyncio.run(send_telegram_message(user_input))
