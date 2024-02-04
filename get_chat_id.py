#!/usr/bin/env python3
import asyncio
from telegram import Bot

# This will only work if you've interacted with your bot recently
# If it doesn't work, try messaging your bot in the chat, or removing
# and re-adding.

# Replace 'your_bot_token' with your actual bot token
bot_token = 'your_bot_token'

async def get_chat_id(bot_token):
  try:
    bot = Bot(token=bot_token)
    updates = await bot.get_updates()
    if updates:
      chat_id = updates[0].message.chat_id
      return chat_id
  except Exception as e:
    print(f"An error occurred: {str(e)}")
  return None

async def main():
  chat_id = await get_chat_id(bot_token)
  if chat_id:
    print(f"Your chat ID is: {chat_id}")
  else:
    print("Failed to retrieve chat ID.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())