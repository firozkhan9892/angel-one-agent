"""
Telegram Commands Handler - Process user confirmations and commands
"""

import requests
from logzero import logger


class TelegramCommandHandler:
    """Handle Telegram commands and callback queries"""

    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.approved_trades = []
        self.rejected_trades = []

    def get_updates(self, offset=0):
        """Get latest Telegram updates"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {'offset': offset, 'timeout': 30}
            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()
            return response.json().get('result', [])
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []

    def handle_callback_query(self, query_id, callback_data, notifier):
        """Handle callback button press"""
        try:
            if callback_data.startswith('approve_'):
                trade_id = callback_data.replace('approve_', '')
                trade = notifier.get_pending_trade(trade_id)
                if trade:
                    self.approved_trades.append(trade)
                    notifier.clear_pending_trade(trade_id)
                    self.answer_callback(query_id, f"Trade approved: {trade['symbol']} {trade['action']}")
                    return trade

            elif callback_data.startswith('reject_'):
                trade_id = callback_data.replace('reject_', '')
                trade = notifier.get_pending_trade(trade_id)
                if trade:
                    self.rejected_trades.append(trade)
                    notifier.clear_pending_trade(trade_id)
                    self.answer_callback(query_id, f"Trade rejected: {trade['symbol']} {trade['action']}")
                    return None

        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            self.answer_callback(query_id, "Error processing request")

        return None

    def answer_callback(self, query_id, text):
        """Send callback answer (notification)"""
        try:
            url = f"{self.base_url}/answerCallbackQuery"
            payload = {
                'callback_query_id': query_id,
                'text': text,
                'show_alert': False
            }
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Error answering callback: {e}")

    def get_approved_trade(self):
        """Get next approved trade"""
        if self.approved_trades:
            return self.approved_trades.pop(0)
        return None

    def is_trade_rejected(self, trade_id):
        """Check if trade was rejected"""
        for trade in self.rejected_trades:
            if f"{trade['symbol']}_{trade['action']}" in trade_id:
                return True
        return False
