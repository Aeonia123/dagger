#!/usr/bin/env python3
import asyncio
from datetime import datetime, timedelta
import os
import re
import subprocess
from telegram import Bot
import time
import queue

# Telegram bot settings
TOKEN = <telegram token>
CHAT_ID = <chat id>

LOG_FILE_PATH = '/home/dagger/config.log'
ERROR_LOG_FILE_PATH = '/home/dagger/monitor_error_log.txt'
ERROR_THRESHOLD = 10  # Adjust as needed
DOWN_THRESHOLD = 5  # Adjust as needed
RESTART_WINDOW = timedelta(minutes=1) # The errors or down messages have to happen within this time window 
RESTART_PAUSE = timedelta(minutes=1) # Only try to restart once a minute
MAX_DOWN_MINUTES = timedelta(minutes=1) # Max time between success messages

RESTART_COMMAND = "sudo systemctl restart wield.service"

async def send_telegram_message(message):
	bot = Bot(token=TOKEN)
	try:
		await bot.send_message(chat_id=CHAT_ID, text=message)
	except Exception as e:
		log_error(f"Failed to send Telegram message: {e}")
		# Implement retry logic if needed

def log_error(message):
	with open(ERROR_LOG_FILE_PATH, "a") as error_log:
		error_log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def notify_and_log_error(message):
	log_error(message)
	asyncio.run(send_telegram_message(message))

def errors_within_window(queue, threshold, window, latest_timestamp):
	queue_size = queue.qsize() 
	if (queue.qsize() >= threshold):
		time_diff = latest_timestamp - queue.get()
		if (time_diff <= window):
			# Clear the queue
			while not queue.empty():
				queue.get()
			return True
	return False

def get_timestamp_from_line(line):
	timestamp_datetime = None
	timestamp_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+'
	match = re.search(timestamp_pattern, line)
	if match:
		timestamp_str = match.group(0)
		fmt = "%Y-%m-%dT%H:%M:%S.%f" 
		try:
			timestamp_datetime = datetime.strptime(timestamp_str, fmt)
		except ValueError as v:
			if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
				timestamp_str = timestamp_str[:-(len(v.args[0]) - 26)]
				timestamp_datetime = datetime.strptime(timestamp_str, fmt)
			else:
				raise
	if not timestamp_datetime:
		notify_and_log_error(f"Couldn't get a time stamp from the line: {line}")
	return timestamp_datetime

def maybe_restart_node(last_restart_time):
	restarted = False
	if(datetime.now() - last_restart_time >= RESTART_PAUSE):
		asyncio.run(send_telegram_message(f"*** Restarting node! ***"))
		try:
			result = subprocess.run(RESTART_COMMAND, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
			restarted = True
		except subprocess.CalledProcessError as e:
			notify_and_log_error(f"Error restarting the node: {e}")
	else:
		asyncio.run(send_telegram_message(f"*** Not restarting node, it's too soon! ***"))    
	return restarted

def monitor_log_file():
	last_success_time = datetime.now()
	last_restart_time = datetime.now()
	should_attempt_restart_node = False
	last_size = -1 # Set this to 0 if you want to read the log file from the beginning for testing

	error_timestamp_queue = queue.Queue(maxsize=ERROR_THRESHOLD)
	down_timestamp_queue = queue.Queue(maxsize=DOWN_THRESHOLD)
	while True:
		try:
			if os.path.exists(LOG_FILE_PATH):
				current_size = os.path.getsize(LOG_FILE_PATH)
				# This is the first read after startup, so only check logs that appear from now on.
				# Otherwise we'll alert on all the stuff that happened in the past. 
				if last_size < 0:
					last_size = current_size
				elif current_size < last_size:
					# Log has been rotated or truncated, so start from the beginning
					last_size = 0

				if current_size > last_size:
					with open(LOG_FILE_PATH, 'r') as file:
						file.seek(last_size, 0)
						for line in file:
							if 'is_up=true' in line:
								last_success_time = datetime.now()
							elif 'is_up=false' in line:
								asyncio.run(send_telegram_message(f"Node is down!\n{line}")) # less spammy than errors
								latest_timestamp = get_timestamp_from_line(line) 
								if latest_timestamp:
									down_timestamp_queue.put(latest_timestamp)
									if errors_within_window(down_timestamp_queue, DOWN_THRESHOLD, RESTART_WINDOW, latest_timestamp):
										# The node can switch between up and down. For now, just notify, and see if relying on 
										# time since last success works well.
										asyncio.run(send_telegram_message(f"{DOWN_THRESHOLD} downs detected within {RESTART_WINDOW} mins."))
										# should_attempt_restart_node = True
							if '[ERROR]' in line:
								# asyncio.run(send_telegram_message(f"Node has error!\n{line}")) # This can be very spammy 
								latest_timestamp = get_timestamp_from_line(line)
								if latest_timestamp:        
									error_timestamp_queue.put(latest_timestamp)
									if errors_within_window(error_timestamp_queue, ERROR_THRESHOLD, RESTART_WINDOW, latest_timestamp):
										# Don't restart because peer connection timeout errors are generally ok. Just notify if we
										# get a lot of them. 
										asyncio.run(send_telegram_message(f"{ERROR_THRESHOLD} errors detected within {RESTART_WINDOW} mins."))
										# should_attempt_restart_node = True

				last_size = current_size

				# If it's been MAX_DOWN_MINUTES since the last is_up=true, try to restart
				# This might be enough of a restart signal. Errors happen sporadically during
				# the day, and during turbulent times it's not clear yet if it's better to restart
				# after a few is_up=falses or better to let the node keep trying for a bit.
				time_since_last_success = datetime.now() - last_success_time
				if(time_since_last_success > MAX_DOWN_MINUTES):
						asyncio.run(send_telegram_message(f"No success messages from node in {time_since_last_success}"))
						should_attempt_restart_node = True

				if(should_attempt_restart_node):
					if maybe_restart_node(last_restart_time):
						last_restart_time = datetime.now()
						last_success_time = datetime.now()
						should_attempt_restart_node = False
										 
		except Exception as e:
			notify_and_log_error(f"Error in restart script: {e}")

		time.sleep(1)

if __name__ == "__main__":
		monitor_log_file()