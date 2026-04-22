"""
Simple Telegram Command Listener - Standalone service
"""

import os
import time
import requests
from dotenv import load_dotenv
from logzero import logger, logfile
from datetime import datetime

load_dotenv()

# Setup logging
os.makedirs("logs", exist_ok=True)
logfile(f"logs/telegram_listener_{datetime.now().strftime('%Y%m%d')}.log", maxBytes=5_000_000, backupCount=3)

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
base_url = f"https://api.telegram.org/bot{bot_token}"

def send_reply(text, reply_to_message_id=None):
    """Send reply message"""
    try:
        url = f"{base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'reply_to_message_id': reply_to_message_id
        }
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error sending reply: {e}")
        return False

def handle_command(text):
    """Handle command and return reply"""
    text_lower = text.lower().strip()

    if text_lower == "/help":
        return """Available Commands:

/portfolio - Show all open positions
/dashboard - 7-day performance
/dashboard30 - 30-day performance
/watchlist - Show watchlist
/sentiment - Sentiment analysis
/symbols - Active symbols
/help - Show this help"""

    elif text_lower == "/portfolio":
        return "Portfolio: No open positions"

    elif text_lower == "/dashboard":
        return "Dashboard: 7-day performance data"

    elif text_lower == "/symbols":
        return "Active Symbols: RELIANCE"

    elif text_lower == "/sentiment":
        return "Sentiment: Analyzing..."

    else:
        return "Unknown command. Type /help for available commands."

def main():
    logger.info("Telegram Command Listener Started")
    update_offset = 0

    while True:
        try:
            # Get updates
            url = f"{base_url}/getUpdates"
            params = {'offset': update_offset, 'timeout': 30}
            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()

            updates = response.json().get('result', [])
            if updates:
                logger.info(f"Received {len(updates)} updates")

            for update in updates:
                update_offset = update['update_id'] + 1

                if 'message' in update:
                    message = update['message']
                    if 'text' in message:
                        text = message['text']
                        message_id = message['message_id']

                        logger.info(f"Command received: {text}")

                        reply = handle_command(text)
                        if send_reply(reply, message_id):
                            logger.info(f"Reply sent for: {text}")
                        else:
                            logger.error(f"Failed to send reply for: {text}")

        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
