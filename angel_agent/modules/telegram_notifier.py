"""
Telegram Notifier - Send alerts and handle trade confirmations
"""

import requests
from logzero import logger


class TelegramNotifier:
    """Send Telegram messages and handle trade confirmations"""

    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or ""
        self.chat_id = chat_id or ""
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.pending_trades = {}

    def send_message(self, text):
        """Send plain text message"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def send_startup(self, symbol, interval):
        """Send startup notification"""
        msg = f"Agent Started\nSymbol: {symbol}\nInterval: {interval}"
        return self.send_message(msg)

    def send_signal(self, signal):
        """Send signal notification"""
        msg = f"Signal Generated\nAction: {signal.action}\nPrice: {signal.ltp}\nScore: {signal.score}\nTarget: {signal.target}\nSL: {signal.sl}"
        return self.send_message(msg)

    def send_error(self, error_msg):
        """Send error notification"""
        msg = f"Error: {error_msg}"
        return self.send_message(msg)

    def send_trade_confirmation(self, symbol, action, qty, price, target, sl):
        """Send trade confirmation request with inline buttons"""
        try:
            trade_id = f"{symbol}_{action}_{int(price*100)}"
            self.pending_trades[trade_id] = {
                'symbol': symbol,
                'action': action,
                'qty': qty,
                'price': price,
                'target': target,
                'sl': sl
            }

            msg = f"CONFIRM TRADE?\n\nSymbol: {symbol}\nAction: {action}\nQty: {qty}\nPrice: {price}\nTarget: {target}\nSL: {sl}"

            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': msg,
                'reply_markup': {
                    'inline_keyboard': [
                        [
                            {'text': 'APPROVE', 'callback_data': f'approve_{trade_id}'},
                            {'text': 'REJECT', 'callback_data': f'reject_{trade_id}'}
                        ]
                    ]
                }
            }

            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Error sending confirmation: {e}")
            return False

    def send_position_update(self, symbol, action, qty, price, pnl=None):
        """Send position update"""
        msg = f"Position Update\nSymbol: {symbol}\nAction: {action}\nQty: {qty}\nPrice: {price}"
        if pnl is not None:
            msg += f"\nP&L: {pnl}"
        return self.send_message(msg)

    def send_performance_report(self, metrics):
        """Send performance report"""
        msg = f"Performance Report\nTotal Signals: {metrics['total_signals']}\nWin Rate: {metrics['win_rate']}%\nTotal P&L: {metrics['total_pnl']}\nAvg P&L: {metrics['avg_pnl_per_signal']}"
        return self.send_message(msg)

    def get_pending_trade(self, trade_id):
        """Get pending trade details"""
        return self.pending_trades.get(trade_id)

    def clear_pending_trade(self, trade_id):
        """Clear pending trade"""
        if trade_id in self.pending_trades:
            del self.pending_trades[trade_id]
