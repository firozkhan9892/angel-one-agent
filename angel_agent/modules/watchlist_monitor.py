"""
Watchlist Monitor - Track multiple stocks without trading them
"""

import sqlite3
from datetime import datetime
from logzero import logger


class WatchlistMonitor:
    """Monitor stocks without executing trades"""

    def __init__(self, db_path="data/trading_agent.db"):
        self.db_path = db_path
        self.watchlist = {}
        self._init_watchlist_table()

    def _init_watchlist_table(self):
        """Initialize watchlist table in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT UNIQUE,
                    token TEXT,
                    exchange TEXT,
                    added_date DATETIME,
                    last_price REAL,
                    last_update DATETIME,
                    notes TEXT
                )
            """)

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error initializing watchlist table: {e}")

    def add_to_watchlist(self, symbol, token, exchange="NSE", notes=""):
        """Add symbol to watchlist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO watchlist
                (symbol, token, exchange, added_date, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (symbol, token, exchange, datetime.now(), notes))

            conn.commit()
            conn.close()
            logger.info(f"Added to watchlist: {symbol}")
            return True

        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            return False

    def remove_from_watchlist(self, symbol):
        """Remove symbol from watchlist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol,))

            conn.commit()
            conn.close()
            logger.info(f"Removed from watchlist: {symbol}")
            return True

        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            return False

    def get_watchlist(self):
        """Get all watchlist symbols"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM watchlist ORDER BY added_date DESC")
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results

        except Exception as e:
            logger.error(f"Error getting watchlist: {e}")
            return []

    def update_watchlist_price(self, symbol, price):
        """Update last price for watchlist symbol"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE watchlist
                SET last_price = ?, last_update = ?
                WHERE symbol = ?
            """, (price, datetime.now(), symbol))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Error updating watchlist price: {e}")
            return False

    def get_watchlist_alerts(self, price_change_percent=5.0):
        """Get watchlist symbols with significant price changes"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM watchlist
                WHERE last_price IS NOT NULL
                ORDER BY last_update DESC
            """)

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()

            alerts = []
            for item in results:
                if item['last_price']:
                    alerts.append({
                        'symbol': item['symbol'],
                        'price': item['last_price'],
                        'last_update': item['last_update']
                    })

            return alerts

        except Exception as e:
            logger.error(f"Error getting watchlist alerts: {e}")
            return []

    def get_watchlist_summary(self):
        """Get watchlist summary"""
        watchlist = self.get_watchlist()

        summary = {
            'total_symbols': len(watchlist),
            'symbols': [w['symbol'] for w in watchlist],
            'with_prices': len([w for w in watchlist if w['last_price']]),
            'watchlist': watchlist
        }

        return summary

    def format_watchlist_report(self):
        """Format watchlist as readable report"""
        summary = self.get_watchlist_summary()

        report = f"Watchlist Summary\n"
        report += f"Total Symbols: {summary['total_symbols']}\n"
        report += f"With Prices: {summary['with_prices']}\n\n"

        for item in summary['watchlist']:
            report += f"{item['symbol']}: {item['last_price'] or 'N/A'}\n"

        return report
