"""
Multi-Symbol Manager - Handle multiple stocks simultaneously
"""

import os
from logzero import logger


class MultiSymbolManager:
    """Manage trading across multiple symbols"""

    def __init__(self):
        self.symbols = self._parse_symbols()
        self.symbol_configs = {}
        self._load_symbol_configs()

    def _parse_symbols(self):
        """Parse symbols from environment variable"""
        symbols_str = os.getenv("SYMBOLS", "RELIANCE")
        return [s.strip() for s in symbols_str.split(",")]

    def _load_symbol_configs(self):
        """Load configuration for each symbol"""
        for symbol in self.symbols:
            self.symbol_configs[symbol] = {
                'token': os.getenv(f"{symbol}_TOKEN", "2885"),
                'exchange': os.getenv(f"{symbol}_EXCHANGE", "NSE"),
                'enabled': os.getenv(f"{symbol}_ENABLED", "true").lower() == "true",
                'max_positions': int(os.getenv(f"{symbol}_MAX_POSITIONS", "1")),
                'risk_per_trade': float(os.getenv(f"{symbol}_RISK_PER_TRADE", "0.02"))
            }

    def get_active_symbols(self):
        """Get list of active symbols"""
        return [s for s in self.symbols if self.symbol_configs[s]['enabled']]

    def get_symbol_config(self, symbol):
        """Get configuration for a symbol"""
        return self.symbol_configs.get(symbol, {})

    def is_symbol_enabled(self, symbol):
        """Check if symbol is enabled for trading"""
        return self.symbol_configs.get(symbol, {}).get('enabled', False)

    def get_all_symbols(self):
        """Get all configured symbols"""
        return self.symbols

    def add_symbol(self, symbol, token, exchange="NSE"):
        """Add new symbol to trading list"""
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            self.symbol_configs[symbol] = {
                'token': token,
                'exchange': exchange,
                'enabled': True,
                'max_positions': 1,
                'risk_per_trade': 0.02
            }
            logger.info(f"Added symbol: {symbol}")
            return True
        return False

    def remove_symbol(self, symbol):
        """Remove symbol from trading list"""
        if symbol in self.symbols:
            self.symbols.remove(symbol)
            del self.symbol_configs[symbol]
            logger.info(f"Removed symbol: {symbol}")
            return True
        return False

    def enable_symbol(self, symbol):
        """Enable trading for a symbol"""
        if symbol in self.symbol_configs:
            self.symbol_configs[symbol]['enabled'] = True
            logger.info(f"Enabled: {symbol}")
            return True
        return False

    def disable_symbol(self, symbol):
        """Disable trading for a symbol"""
        if symbol in self.symbol_configs:
            self.symbol_configs[symbol]['enabled'] = False
            logger.info(f"Disabled: {symbol}")
            return True
        return False
