"""
Performance Dashboard - Daily/weekly/monthly P&L charts and statistics
"""

import sqlite3
from datetime import datetime, timedelta
from logzero import logger


class PerformanceDashboard:
    """Generate performance reports and statistics"""

    def __init__(self, db_path="data/trading_agent.db"):
        self.db_path = db_path

    def get_daily_performance(self, days=30):
        """Get daily P&L for last N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            cursor.execute("""
                SELECT
                    DATE(timestamp) as date,
                    COUNT(*) as signals,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
                    SUM(pnl) as daily_pnl
                FROM signals
                WHERE timestamp >= ? AND status = 'CLOSED'
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """, (start_date,))

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results

        except Exception as e:
            logger.error(f"Error getting daily performance: {e}")
            return []

    def get_monthly_performance(self, months=12):
        """Get monthly P&L for last N months"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            start_date = (datetime.now() - timedelta(days=months*30)).strftime('%Y-%m')

            cursor.execute("""
                SELECT
                    strftime('%Y-%m', timestamp) as month,
                    COUNT(*) as signals,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(pnl) as monthly_pnl
                FROM signals
                WHERE strftime('%Y-%m', timestamp) >= ? AND status = 'CLOSED'
                GROUP BY strftime('%Y-%m', timestamp)
                ORDER BY month DESC
            """, (start_date,))

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results

        except Exception as e:
            logger.error(f"Error getting monthly performance: {e}")
            return []

    def get_symbol_performance(self, symbol, days=30):
        """Get performance for specific symbol"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            cursor.execute("""
                SELECT
                    symbol,
                    COUNT(*) as total_signals,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
                    SUM(pnl) as total_pnl,
                    AVG(pnl) as avg_pnl,
                    MAX(pnl) as max_win,
                    MIN(pnl) as max_loss
                FROM signals
                WHERE symbol = ? AND timestamp >= ? AND status = 'CLOSED'
                GROUP BY symbol
            """, (symbol, start_date))

            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Error getting symbol performance: {e}")
            return None

    def get_win_rate_trend(self, days=30):
        """Get win rate trend over time"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            cursor.execute("""
                SELECT
                    DATE(timestamp) as date,
                    ROUND(SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as win_rate
                FROM signals
                WHERE timestamp >= ? AND status = 'CLOSED'
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            """, (start_date,))

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results

        except Exception as e:
            logger.error(f"Error getting win rate trend: {e}")
            return []

    def get_cumulative_pnl(self, days=30):
        """Get cumulative P&L over time"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            cursor.execute("""
                SELECT
                    DATE(timestamp) as date,
                    SUM(SUM(pnl)) OVER (ORDER BY DATE(timestamp)) as cumulative_pnl
                FROM signals
                WHERE timestamp >= ? AND status = 'CLOSED'
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            """, (start_date,))

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results

        except Exception as e:
            logger.error(f"Error getting cumulative P&L: {e}")
            return []

    def get_dashboard_summary(self, days=30):
        """Get complete dashboard summary"""
        daily_perf = self.get_daily_performance(days)
        monthly_perf = self.get_monthly_performance(12)
        win_rate_trend = self.get_win_rate_trend(days)
        cumulative_pnl = self.get_cumulative_pnl(days)

        total_signals = sum(d['signals'] for d in daily_perf)
        total_wins = sum(d['wins'] for d in daily_perf)
        total_pnl = sum(d['daily_pnl'] for d in daily_perf)

        return {
            'period_days': days,
            'total_signals': total_signals,
            'total_wins': total_wins,
            'win_rate': (total_wins / total_signals * 100) if total_signals > 0 else 0,
            'total_pnl': total_pnl,
            'daily_performance': daily_perf,
            'monthly_performance': monthly_perf,
            'win_rate_trend': win_rate_trend,
            'cumulative_pnl': cumulative_pnl
        }

    def format_dashboard_report(self, days=30):
        """Format dashboard as readable report"""
        summary = self.get_dashboard_summary(days)

        report = f"Performance Dashboard ({days} days)\n"
        report += f"Total Signals: {summary['total_signals']}\n"
        report += f"Wins: {summary['total_wins']}\n"
        report += f"Win Rate: {summary['win_rate']:.2f}%\n"
        report += f"Total P&L: {summary['total_pnl']:.2f}\n"

        if summary['daily_performance']:
            latest = summary['daily_performance'][0]
            report += f"\nToday: {latest['daily_pnl']:.2f} ({latest['signals']} signals)\n"

        return report
