"""
Advanced Risk Controls - Stop-loss adjustment, trailing stops, position scaling
"""

from logzero import logger


class AdvancedRiskControls:
    """Advanced risk management features"""

    def __init__(self, account_size=10000, risk_per_trade=0.02):
        self.account_size = account_size
        self.risk_per_trade = risk_per_trade
        self.positions = {}
        self.max_drawdown = 0.15

    def calculate_position_size_kelly(self, win_rate, avg_win, avg_loss):
        """Calculate position size using Kelly Criterion"""
        if avg_loss == 0:
            return 0

        kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        kelly_fraction = max(0, min(kelly_fraction, 0.25))

        position_size = self.account_size * kelly_fraction
        return position_size

    def calculate_trailing_stop(self, entry_price, current_price, atr, trail_percent=0.02):
        """Calculate trailing stop level"""
        if current_price > entry_price:
            trail_amount = max(atr * 1.5, current_price * trail_percent)
            trailing_sl = current_price - trail_amount
            return max(trailing_sl, entry_price * 0.98)
        return entry_price * 0.97

    def calculate_dynamic_sl(self, entry_price, atr, risk_percent=0.02):
        """Calculate dynamic stop-loss based on ATR"""
        sl_distance = atr * 2
        sl_price = entry_price - sl_distance
        return max(sl_price, entry_price * (1 - risk_percent))

    def calculate_dynamic_target(self, entry_price, atr, reward_ratio=2.0):
        """Calculate dynamic target based on ATR and reward ratio"""
        sl_distance = atr * 2
        target_distance = sl_distance * reward_ratio
        return entry_price + target_distance

    def scale_position(self, current_position, profit_percent, scale_levels=None):
        """Scale out of position at profit levels"""
        if scale_levels is None:
            scale_levels = [0.25, 0.50, 0.75]

        scale_out = {}
        for level in scale_levels:
            if profit_percent >= level * 100:
                qty_to_sell = int(current_position * 0.25)
                scale_out[level] = qty_to_sell

        return scale_out

    def check_max_drawdown(self, current_balance, peak_balance):
        """Check if max drawdown threshold exceeded"""
        if peak_balance == 0:
            return False

        drawdown = (peak_balance - current_balance) / peak_balance
        return drawdown > self.max_drawdown

    def adjust_position_for_volatility(self, base_qty, current_atr, avg_atr):
        """Adjust position size based on volatility"""
        if avg_atr == 0:
            return base_qty

        volatility_ratio = current_atr / avg_atr
        adjusted_qty = int(base_qty / volatility_ratio)
        return max(1, adjusted_qty)

    def calculate_risk_reward_ratio(self, entry_price, sl_price, target_price):
        """Calculate risk-reward ratio"""
        risk = abs(entry_price - sl_price)
        reward = abs(target_price - entry_price)

        if risk == 0:
            return 0

        return reward / risk

    def validate_trade_setup(self, entry_price, sl_price, target_price, min_rr=1.5):
        """Validate if trade setup meets minimum risk-reward"""
        rr = self.calculate_risk_reward_ratio(entry_price, sl_price, target_price)
        return rr >= min_rr

    def get_position_status(self, symbol, entry_price, current_price, qty):
        """Get detailed position status"""
        pnl = (current_price - entry_price) * qty
        pnl_percent = ((current_price - entry_price) / entry_price) * 100

        return {
            'symbol': symbol,
            'entry_price': entry_price,
            'current_price': current_price,
            'qty': qty,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'status': 'PROFIT' if pnl > 0 else 'LOSS' if pnl < 0 else 'BREAKEVEN'
        }
