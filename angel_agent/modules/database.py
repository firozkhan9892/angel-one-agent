"""
Database Manager - SQLite database operations
"""

import sqlite3
import os
from datetime import datetime
from logzero import logger


class Database:
    """Manage SQLite database for signals and positions"""

    def __init__(self, db_path="data/trading_agent.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Signals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY,
                    timestamp DATETIME,
                    symbol TEXT,
                    ltp REAL,
                    action TEXT,
                    score INTEGER,
                    confidence TEXT,
                    target REAL,
                    sl REAL,
                    entry_price REAL,
                    exit_price REAL,
                    pnl REAL,
                    status TEXT
                )
            """)

            # Positions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT,
                    qty INTEGER,
                    entry_price REAL,
                    entry_time DATETIME,
                    exit_price REAL,
                    exit_time DATETIME,
                    pnl REAL,
                    status TEXT
                )
            """)

            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY,
                    date DATE,
                    total_signals INTEGER,
                    winning_signals INTEGER,
                    losing_signals INTEGER,
                    win_rate REAL,
                    total_pnl REAL,
                    max_drawdown REAL
                )
            """)

            conn.commit()
            conn.close()
            logger.info("Database initialized")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    def save_signal(self, symbol, ltp, action, score, confidence, target, sl):
        """Save signal to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO signals
                (timestamp, symbol, ltp, action, score, confidence, target, sl, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now(), symbol, ltp, action, score, confidence, target, sl, "OPEN"))

            conn.commit()
            conn.close()
            logger.info(f"Signal saved: {symbol} {action}")
            return True

        except Exception as e:
            logger.error(f"Error saving signal: {e}")
            return False

    def get_signals(self, symbol=None, days=30):
        """Get signals from database"""
        try:
            from datetime import timedelta

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            if symbol:
                cursor.execute("""
                    SELECT * FROM signals
                    WHERE symbol = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                """, (symbol, start_date))
            else:
                cursor.execute("""
                    SELECT * FROM signals
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (start_date,))

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results

        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            return []

    def update_signal_pnl(self, signal_id, exit_price, pnl):
        """Update signal with exit price and P&L"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE signals
                SET exit_price = ?, pnl = ?, status = 'CLOSED'
                WHERE id = ?
            """, (exit_price, pnl, signal_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Error updating signal: {e}")
            return False

    def close(self):
        """Close database connection"""
        logger.info("Database closed")
