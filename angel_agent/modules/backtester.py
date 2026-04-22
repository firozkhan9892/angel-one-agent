"""
Backtester - Historical signal replay and performance analysis
"""

import sqlite3
from datetime import datetime, timedelta
from modules.indicators import IndicatorEngine
from modules.signal_generator import SignalGenerator


class Backtester:
    """Replay signals on historical data and calculate performance metrics"""

    def __init__(self, db_path="data/trading_agent.db"):
        self.db_path = db_path
        self.signal_gen = SignalGenerator()

    def get_historical_signals(self, symbol, days=30):
        """Fetch historical signals from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        cursor.execute("""
            SELECT * FROM signals
            WHERE symbol = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        """, (symbol, start_date))

        signals = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return signals

    def calculate_metrics(self, symbol, days=30):
        """Calculate performance metrics for a symbol"""
        signals = self.get_historical_signals(symbol, days)

        if not signals:
            return {
                'symbol': symbol,
                'total_signals': 0,
                'winning_signals': 0,
                'losing_signals': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'max_win': 0,
                'max_loss': 0,
                'sharpe_ratio': 0
            }

        # Count wins/losses
        winning = [s for s in signals if s.get('pnl', 0) > 0]
        losing = [s for s in signals if s.get('pnl', 0) < 0]

        total_pnl = sum(s.get('pnl', 0) for s in signals)
        pnls = [s.get('pnl', 0) for s in signals if s.get('pnl', 0) != 0]

        # Calculate Sharpe ratio (simplified)
        if len(pnls) > 1:
            mean_pnl = sum(pnls) / len(pnls)
            variance = sum((p - mean_pnl) ** 2 for p in pnls) / len(pnls)
            std_dev = variance ** 0.5
            sharpe = (mean_pnl / std_dev * (252 ** 0.5)) if std_dev > 0 else 0
        else:
            sharpe = 0

        win_rate = len(winning) / len(signals) * 100 if signals else 0

        return {
            'symbol': symbol,
            'total_signals': len(signals),
            'winning_signals': len(winning),
            'losing_signals': len(losing),
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'avg_pnl': round(total_pnl / len(signals), 2) if signals else 0,
            'max_win': round(max(pnls, default=0), 2),
            'max_loss': round(min(pnls, default=0), 2),
            'sharpe_ratio': round(sharpe, 2)
        }

    def get_portfolio_performance(self, days=30):
        """Get overall portfolio performance"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        cursor.execute("""
            SELECT
                COUNT(*) as total_signals,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_signals,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_signals,
                SUM(pnl) as total_pnl
            FROM signals
            WHERE timestamp >= ?
        """, (start_date,))

        row = cursor.fetchone()
        conn.close()

        total = row['total_signals'] or 0
        wins = row['winning_signals'] or 0
        losses = row['losing_signals'] or 0
        pnl = row['total_pnl'] or 0

        return {
            'period_days': days,
            'total_signals': total,
            'winning_signals': wins,
            'losing_signals': losses,
            'win_rate': round(wins / total * 100, 2) if total > 0 else 0,
            'total_pnl': round(pnl, 2),
            'avg_pnl_per_signal': round(pnl / total, 2) if total > 0 else 0
        }
