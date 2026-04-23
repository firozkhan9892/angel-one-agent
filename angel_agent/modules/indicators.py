"""
Technical Indicators Engine
Computes various technical indicators for trading
"""

import pandas as pd
import numpy as np
from logzero import logger

class IndicatorEngine:
    @staticmethod
    def compute_all(df):
        """Compute all technical indicators"""
        try:
            df = IndicatorEngine._add_sma(df)
            df = IndicatorEngine._add_ema(df)
            df = IndicatorEngine._add_rsi(df)
            df = IndicatorEngine._add_macd(df)
            df = IndicatorEngine._add_bollinger_bands(df)
            df = IndicatorEngine._add_atr(df)
            df = IndicatorEngine._add_stochastic(df)
            df = IndicatorEngine._add_volume_indicators(df)
            return df
        except Exception as e:
            logger.error(f"Error computing indicators: {e}")
            return df

    @staticmethod
    def _add_sma(df, periods=[20, 50]):
        """Simple Moving Average"""
        for period in periods:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
        return df

    @staticmethod
    def _add_ema(df, periods=[12, 26]):
        """Exponential Moving Average"""
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        return df

    @staticmethod
    def _add_rsi(df, period=14):
        """Relative Strength Index"""
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df

    @staticmethod
    def _add_macd(df, fast=12, slow=26, signal=9):
        """MACD - Moving Average Convergence Divergence"""
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        return df

    @staticmethod
    def _add_bollinger_bands(df, period=20, std_dev=2):
        """Bollinger Bands"""
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        bb_std = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (bb_std * std_dev)
        return df

    @staticmethod
    def _add_atr(df, period=14):
        """Average True Range"""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=period).mean()
        return df

    @staticmethod
    def _add_stochastic(df, period=14, smooth=3):
        """Stochastic Oscillator"""
        low_min = df['low'].rolling(window=period).min()
        high_max = df['high'].rolling(window=period).max()
        df['stoch_k'] = 100 * (df['close'] - low_min) / (high_max - low_min)
        df['stoch_d'] = df['stoch_k'].rolling(window=smooth).mean()
        return df

    @staticmethod
    def _add_volume_indicators(df):
        """Volume-based indicators"""
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        return df

    @staticmethod
    def get_latest_signals(df):
        """Get latest indicator values for signal generation"""
        if df.empty or len(df) < 50:
            return {}

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        return {
            "rsi": latest.get("rsi", 50),
            "macd": latest.get("macd", 0),
            "macd_signal": latest.get("macd_signal", 0),
            "macd_hist": latest.get("macd_hist", 0),
            "sma_20": latest.get("sma_20", 0),
            "sma_50": latest.get("sma_50", 0),
            "bb_upper": latest.get("bb_upper", 0),
            "bb_lower": latest.get("bb_lower", 0),
            "bb_middle": latest.get("bb_middle", 0),
            "atr": latest.get("atr", 0),
            "stoch_k": latest.get("stoch_k", 50),
            "stoch_d": latest.get("stoch_d", 50),
            "close": latest.get("close", 0),
            "volume_ratio": latest.get("volume_ratio", 1),
            "prev_rsi": prev.get("rsi", 50),
            "prev_macd_hist": prev.get("macd_hist", 0)
        }