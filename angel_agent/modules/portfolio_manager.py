"""
Portfolio Manager - Track positions and P&L
"""

import sqlite3
from datetime import datetime
from logzero import logger


class PortfolioManager:
    """Manage trading positions and calculate P&L"""

    def __init__(self, db):
        self.db = db
        self._init_positions_table()

    def _init_positions_table(self):
        """Initialize positions table"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()

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
                    status TEXT,
                    UNIQUE(symbol, entry_time)
                )
            """)

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error initializing positions table: {e}")

    def open_position(self, symbol, qty, entry_price, signal):
        """Open new position"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO positions
                (symbol, qty, entry_price, entry_time, status)
                VALUES (?, ?, ?, ?, ?)
            """, (symbol, qty, entry_price, datetime.now(), "OPEN"))

            conn.commit()
            conn.close()
            logger.info(f"Opened position: {symbol} {qty} @ {entry_price}")
            return True

        except Exception as e:
            logger.error(f"Error opening position: {e}")
            return False

    def close_position(self, symbol, exit_price):
        """Close open position"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM positions
                WHERE symbol = ? AND status = 'OPEN'
                ORDER BY entry_time DESC
                LIMIT 1
            """, (symbol,))

            position = cursor.fetchone()
            if not position:
                conn.close()
                return None

            pnl = (exit_price - position['entry_price']) * position['qty']

            cursor.execute("""
                UPDATE positions
                SET exit_price = ?, exit_time = ?, pnl = ?, status = 'CLOSED'
                WHERE id = ?
            """, (exit_price, datetime.now(), pnl, position['id']))

            conn.commit()
            conn.close()

            logger.info(f"Closed position: {symbol} P&L: {pnl}")
            return {
                'symbol': symbol,
                'qty': position['qty'],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'pnl': pnl
            }

        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return None

    def get_position(self, symbol):
        """Get specific open position"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM positions
                WHERE symbol = ? AND status = 'OPEN'
                ORDER BY entry_time DESC
                LIMIT 1
            """, (symbol,))

            position = cursor.fetchone()
            conn.close()

            if position:
                return dict(position)
            return None

        except Exception as e:
            logger.error(f"Error getting position: {e}")
            return None

    def get_all_positions(self):
        """Get all open positions"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM positions
                WHERE status = 'OPEN'
                ORDER BY entry_time DESC
            """)

            positions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return positions

        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []

    def get_portfolio_summary(self):
        """Get portfolio summary"""
        try:
            positions = self.get_all_positions()
            total_pnl = 0
            total_qty = 0

            for pos in positions:
                total_qty += pos['qty']
                total_pnl += pos.get('pnl', 0)

            return {
                'open_positions': len(positions),
                'total_qty': total_qty,
                'total_pnl': total_pnl,
                'positions': positions
            }

        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {}

    def get_closed_positions(self, days=30):
        """Get closed positions from last N days"""
        try:
            from datetime import timedelta

            conn = sqlite3.connect(self.db.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            cursor.execute("""
                SELECT * FROM positions
                WHERE status = 'CLOSED' AND exit_time >= ?
                ORDER BY exit_time DESC
            """, (start_date,))

            positions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return positions

        except Exception as e:
            logger.error(f"Error getting closed positions: {e}")
            return []
