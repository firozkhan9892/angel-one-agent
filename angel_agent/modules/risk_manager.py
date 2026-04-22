"""
Risk Manager - Position sizing, drawdown tracking, risk controls
"""

import sqlite3
from datetime import datetime
from logzero import logger


class RiskManager:
    """Manage risk, position sizing, and drawdown tracking"""

    def __init__(self, account_size=10000, risk_per_trade=0.02, max_drawdown=0.15):
        self.account_size = account_size
        self.initial_balance = account_size
        self.current_balance = account_size
        self.peak_balance = account_size
        self.risk_per_trade = risk_per_trade
        self.max_drawdown_threshold = max_drawdown
        self.trades_today = 0

    def calculate_position_size(self, entry_price, sl_price):
        """Calculate position size based on risk"""
        if entry_price == 0 or sl_price == 0:
            return 0

        risk_amount = self.current_balance * self.risk_per_trade
        price_risk = abs(entry_price - sl_price)

        if price_risk == 0:
            return 0

        qty = int(risk_amount / price_risk)
        return max(1, qty)

    def update_balance(self, pnl):
        """Update account balance after trade"""
        self.current_balance += pnl
        if self.current_balance > self.peak_balance:
            self.peak_balance = self.current_balance
        logger.info(f"Balance updated: {self.current_balance} (P&L: {pnl})")

    def get_current_drawdown(self):
        """Get current drawdown percentage"""
        if self.peak_balance == 0:
            return 0
        drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        return drawdown

    def get_max_drawdown(self):
        """Get maximum drawdown from peak"""
        return self.get_current_drawdown()

    def should_trade(self):
        """Check if trading should continue"""
        drawdown = self.get_current_drawdown()
        if drawdown > self.max_drawdown_threshold:
            logger.warning(f"Drawdown {drawdown:.2%} exceeds threshold {self.max_drawdown_threshold:.2%}")
            return False
        return True

    def get_risk_metrics(self):
        """Get current risk metrics"""
        drawdown = self.get_current_drawdown()
        return {
            'current_balance': self.current_balance,
            'peak_balance': self.peak_balance,
            'initial_balance': self.initial_balance,
            'drawdown_percent': drawdown * 100,
            'drawdown_threshold': self.max_drawdown_threshold * 100,
            'risk_per_trade': self.risk_per_trade * 100,
            'trading_allowed': self.should_trade()
        }

    def reset_daily_trades(self):
        """Reset daily trade counter"""
        self.trades_today = 0

    def increment_trade_count(self):
        """Increment daily trade counter"""
        self.trades_today += 1
