"""
LSTM-based price direction predictor
"""

import numpy as np
from collections import deque


class PricePredictor:
    """Simple price direction predictor using momentum and trend analysis"""

    def __init__(self, lookback=20):
        self.lookback = lookback
        self.price_history = deque(maxlen=lookback)

    def add_price(self, close_price):
        """Add price to history"""
        self.price_history.append(close_price)

    def predict_next_candle(self, df):
        """
        Predict next candle direction (UP/DOWN)
        Returns: direction, confidence (0-1)
        """
        if len(df) < self.lookback:
            return "NEUTRAL", 0.5

        closes = df['close'].tail(self.lookback).tolist()

        # Calculate momentum
        momentum = (closes[-1] - closes[0]) / closes[0]

        # Calculate trend strength (RSI-like)
        gains = sum(max(0, closes[i] - closes[i-1]) for i in range(1, len(closes)))
        losses = sum(max(0, closes[i-1] - closes[i]) for i in range(1, len(closes)))

        if losses == 0:
            trend_strength = 1.0
        else:
            rs = gains / losses
            trend_strength = rs / (1 + rs)

        # Predict direction
        if momentum > 0.002:  # 0.2% threshold
            direction = "UP"
            confidence = min(0.95, 0.5 + trend_strength * 0.45)
        elif momentum < -0.002:
            direction = "DOWN"
            confidence = min(0.95, 0.5 + trend_strength * 0.45)
        else:
            direction = "NEUTRAL"
            confidence = 0.5

        return direction, confidence

    def get_prediction_score(self, df):
        """Get prediction score for signal generation (-30 to +30)"""
        direction, confidence = self.predict_next_candle(df)

        if direction == "UP":
            return int(30 * confidence)
        elif direction == "DOWN":
            return int(-30 * confidence)
        else:
            return 0
