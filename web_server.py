"""
Web Server + Telegram Command Handler - Keeps app alive on Render
"""

import os
import threading
import time
import requests
from flask import Flask, request
from dotenv import load_dotenv
from logzero import logger, logfile
from datetime import datetime

load_dotenv()

# Setup logging
os.makedirs("logs", exist_ok=True)
logfile(f"logs/web_server_{datetime.now().strftime('%Y%m%d')}.log", maxBytes=5_000_000, backupCount=3)

app = Flask(__name__)

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
base_url = f"https://api.telegram.org/bot{bot_token}"

update_offset = 0

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

/portfolio - Show positions
/dashboard - 7-day performance
/symbols - Active symbols
/sentiment - Sentiment analysis
/watchlist - Watchlist
/status - Agent status
/help - Show this help"""

    elif text_lower == "/portfolio":
        return "Portfolio: No open positions"

    elif text_lower == "/dashboard":
        return "Dashboard: 7-day performance data"

    elif text_lower == "/symbols":
        return "Active Symbols: RELIANCE"

    elif text_lower == "/sentiment":
        return "Sentiment: Analyzing..."

    elif text_lower == "/watchlist":
        return "Watchlist: Empty"

    elif text_lower == "/status":
        return "Agent Status: Running"

    else:
        return "Unknown command. Type /help for available commands."

def telegram_listener():
    """Listen for Telegram updates in background"""
    global update_offset
    logger.info("Telegram listener started")

    while True:
        try:
            url = f"{base_url}/getUpdates"
            params = {'offset': update_offset, 'timeout': 30}
            response = requests.get(url, params=params, timeout=35)
            updates = response.json().get('result', [])

            if updates:
                logger.info(f"Received {len(updates)} updates")

            for update in updates:
                update_offset = update['update_id'] + 1

                if 'message' in update and 'text' in update['message']:
                    message = update['message']
                    text = message['text']
                    message_id = message['message_id']

                    logger.info(f"Command: {text}")

                    reply = handle_command(text)
                    if send_reply(reply, message_id):
                        logger.info(f"Reply sent for: {text}")
                    else:
                        logger.error(f"Failed to send reply for: {text}")

        except Exception as e:
            logger.error(f"Error in telegram listener: {e}")
            time.sleep(5)

@app.route('/')
def health():
    """Health check endpoint"""
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}, 200

@app.route('/health')
def health_check():
    """Health check for Render"""
    return {'status': 'running'}, 200

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    """Webhook for Telegram updates"""
    try:
        data = request.json
        if 'message' in data and 'text' in data['message']:
            message = data['message']
            text = message['text']
            message_id = message['message_id']

            logger.info(f"Webhook command: {text}")

            reply = handle_command(text)
            if send_reply(reply, message_id):
                logger.info(f"Webhook reply sent for: {text}")

        return {'ok': True}, 200
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return {'ok': False, 'error': str(e)}, 500

if __name__ == '__main__':
    # Start Telegram listener in background thread
    listener_thread = threading.Thread(target=telegram_listener, daemon=True)
    listener_thread.start()
    logger.info("Started Telegram listener thread")

    # Start Flask app
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
