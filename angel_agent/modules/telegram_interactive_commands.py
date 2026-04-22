"""
Telegram Interactive Commands - Send commands and get replies
"""

import requests
from logzero import logger


class TelegramInteractiveCommands:
    """Handle interactive Telegram commands with replies"""

    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def get_updates(self, offset=0, timeout=30):
        """Get latest Telegram updates"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {'offset': offset, 'timeout': timeout}
            response = requests.get(url, params=params, timeout=timeout + 5)
            response.raise_for_status()
            return response.json().get('result', [])
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []

    def send_reply(self, text, reply_to_message_id=None):
        """Send reply message"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'reply_to_message_id': reply_to_message_id
            }
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending reply: {e}")
            return False

    def handle_text_command(self, text, message_id, portfolio, dashboard, watchlist, sentiment, symbol_mgr):
        """Handle text commands and return reply"""
        text_lower = text.lower().strip()

        # Portfolio commands
        if text_lower == "/portfolio":
            return self._get_portfolio_status(portfolio)

        elif text_lower.startswith("/position "):
            symbol = text_lower.replace("/position ", "").upper()
            return self._get_position_status(portfolio, symbol)

        # Dashboard commands
        elif text_lower == "/dashboard":
            return dashboard.format_dashboard_report(days=7)

        elif text_lower == "/dashboard30":
            return dashboard.format_dashboard_report(days=30)

        # Watchlist commands
        elif text_lower == "/watchlist":
            return watchlist.format_watchlist_report()

        elif text_lower.startswith("/add_watchlist "):
            symbol = text_lower.replace("/add_watchlist ", "").upper()
            watchlist.add_to_watchlist(symbol, "0", "NSE")
            return f"Added {symbol} to watchlist"

        elif text_lower.startswith("/remove_watchlist "):
            symbol = text_lower.replace("/remove_watchlist ", "").upper()
            watchlist.remove_from_watchlist(symbol)
            return f"Removed {symbol} from watchlist"

        # Sentiment commands
        elif text_lower == "/sentiment":
            symbols = symbol_mgr.get_active_symbols()
            return sentiment.get_sentiment_report(symbols)

        elif text_lower.startswith("/sentiment "):
            symbol = text_lower.replace("/sentiment ", "").upper()
            sentiment_val, score = sentiment.get_news_sentiment(symbol)
            return f"{symbol} Sentiment: {sentiment_val} (Score: {score:.2f})"

        # Symbol commands
        elif text_lower == "/symbols":
            symbols = symbol_mgr.get_active_symbols()
            return f"Active Symbols: {', '.join(symbols)}"

        elif text_lower.startswith("/enable "):
            symbol = text_lower.replace("/enable ", "").upper()
            symbol_mgr.enable_symbol(symbol)
            return f"Enabled {symbol}"

        elif text_lower.startswith("/disable "):
            symbol = text_lower.replace("/disable ", "").upper()
            symbol_mgr.disable_symbol(symbol)
            return f"Disabled {symbol}"

        # Help command
        elif text_lower == "/help":
            return self._get_help_text()

        else:
            return "Unknown command. Type /help for available commands."

    def _get_portfolio_status(self, portfolio):
        """Get portfolio status"""
        try:
            positions = portfolio.get_all_positions()
            if not positions:
                return "No open positions"

            report = "Portfolio Status:\n\n"
            total_pnl = 0

            for pos in positions:
                report += f"{pos['symbol']}: {pos['qty']} @ {pos['entry_price']}\n"
                report += f"P&L: {pos.get('pnl', 0):.2f}\n\n"
                total_pnl += pos.get('pnl', 0)

            report += f"Total P&L: {total_pnl:.2f}"
            return report

        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            return "Error fetching portfolio"

    def _get_position_status(self, portfolio, symbol):
        """Get specific position status"""
        try:
            position = portfolio.get_position(symbol)
            if not position:
                return f"No open position for {symbol}"

            report = f"Position: {symbol}\n"
            report += f"Qty: {position['qty']}\n"
            report += f"Entry: {position['entry_price']}\n"
            report += f"Current: {position.get('current_price', 'N/A')}\n"
            report += f"P&L: {position.get('pnl', 0):.2f}\n"
            report += f"P&L %: {position.get('pnl_percent', 0):.2f}%"

            return report

        except Exception as e:
            logger.error(f"Error getting position: {e}")
            return f"Error fetching position for {symbol}"

    def _get_help_text(self):
        """Get help text with all commands"""
        help_text = """Available Commands:

Portfolio:
/portfolio - Show all open positions
/position SYMBOL - Show specific position

Dashboard:
/dashboard - 7-day performance
/dashboard30 - 30-day performance

Watchlist:
/watchlist - Show watchlist
/add_watchlist SYMBOL - Add to watchlist
/remove_watchlist SYMBOL - Remove from watchlist

Sentiment:
/sentiment - Sentiment for all symbols
/sentiment SYMBOL - Sentiment for specific symbol

Symbols:
/symbols - Show active symbols
/enable SYMBOL - Enable trading for symbol
/disable SYMBOL - Disable trading for symbol

/help - Show this help"""

        return help_text

    def process_message(self, message, portfolio, dashboard, watchlist, sentiment, symbol_mgr):
        """Process incoming message and return reply"""
        try:
            if 'text' not in message:
                return None

            text = message['text']
            message_id = message['message_id']

            logger.info(f"Processing command: {text}")
            reply = self.handle_text_command(text, message_id, portfolio, dashboard, watchlist, sentiment, symbol_mgr)
            logger.info(f"Reply generated: {reply[:50] if reply else 'None'}")
            return reply
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Error: {str(e)}"
