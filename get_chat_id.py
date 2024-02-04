#!/usr/bin/env python3
import asyncio
from telegram import Bot

# This will only work if you've interacted with your bot recently
# If it doesn't work, try messaging your bot in the chat, or removing
# and re-adding.

# Replace 'your_bot_token' with your actual bot token
bot_token = 'your_bot_token'

async def get_chat_id(bot_token):
  chat_ids = []
  try:
    bot = Bot(token=bot_token)
    updates = await bot.get_updates()

    for update in updates:
      if hasattr(update, "my_chat_member") and update.my_chat_member is not None:  
        chat_id = update.my_chat_member.chat.id
        chat_ids.append(chat_id)
      if hasattr(update, "message") and update.message is not None:
          chat_id = update.message.chat.id
          chat_ids.append(chat_id)

  except Exception as e:
    print(f"An error occurred: {str(e)}")

  # Remove duplicates
  return set(chat_ids)

async def main():
  chat_ids = await get_chat_id(bot_token)
  if chat_ids:
    for chat_id in chat_ids:
      print(f"Your chat ID is: {chat_id}")
  else:
    print("Failed to retrieve chat ID.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())