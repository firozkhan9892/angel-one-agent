"""
Trading Signal Generator
Generates BUY/SELL/HOLD signals based on technical indicators
"""

import pandas as pd
from dataclasses import dataclass
from logzero import logger

@dataclass
class TradingSignal:
    action: str  # BUY, SELL, HOLD
    ltp: float
    score: float  # -100 to 100
    confidence: float  # 0 to 100
    target: float = 0
    sl: float = 0
    reason: str = ""

class SignalGenerator:
    def __init__(self):
        self.min_confidence = 50

    def generate(self, df):
        """Generate trading signal from indicator data"""
        try:
            if df.empty or len(df) < 50:
                return TradingSignal("HOLD", 0, 0, 0, reason="Insufficient data")

            # Get latest indicator values
            signals = self._analyze_indicators(df)
            latest = df.iloc[-1]
            ltp = latest.get("close", 0)

            # Calculate overall score
            score = self._calculate_score(signals)
            confidence = self._calculate_confidence(signals)

            # Determine action
            action = self._determine_action(score, confidence, signals)
            reason = self._generate_reason(action, signals)

            # Calculate target and stop-loss
            target, sl = self._calculate_levels(ltp, signals, action)

            return TradingSignal(
                action=action,
                ltp=ltp,
                score=score,
                confidence=confidence,
                target=target,
                sl=sl,
                reason=reason
            )
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return TradingSignal("HOLD", 0, 0, 0, reason=f"Error: {str(e)}")

    def _analyze_indicators(self, df):
        """Analyze all indicators and return signals"""
        from modules.indicators import IndicatorEngine
        return IndicatorEngine.get_latest_signals(df)

    def _calculate_score(self, signals):
        """Calculate overall signal score (-100 to 100)"""
        score = 0

        # RSI (0-100, oversold=buy signal, overbought=sell signal)
        rsi = signals.get("rsi", 50)
        if rsi < 30:
            score += 30  # Oversold - BUY
        elif rsi > 70:
            score -= 30  # Overbought - SELL
        elif rsi < 40:
            score += 15
        elif rsi > 60:
            score -= 15

        # MACD histogram (positive=bullish, negative=bearish)
        macd_hist = signals.get("macd_hist", 0)
        if macd_hist > 0:
            score += 20
        else:
            score -= 20

        # MACD crossover
        prev_macd_hist = signals.get("prev_macd_hist", 0)
        if macd_hist > 0 and prev_macd_hist < 0:
            score += 15  # Bullish crossover
        elif macd_hist < 0 and prev_macd_hist > 0:
            score -= 15  # Bearish crossover

        # Price vs SMA
        close = signals.get("close", 0)
        sma_20 = signals.get("sma_20", 0)
        sma_50 = signals.get("sma_50", 0)

        if close > sma_20:
            score += 10
        else:
            score -= 10

        if close > sma_50:
            score += 10
        else:
            score -= 10

        # Trend alignment (sma_20 > sma_50 = bullish)
        if sma_20 > sma_50:
            score += 10
        else:
            score -= 10

        # Bollinger Bands position
        bb_upper = signals.get("bb_upper", 0)
        bb_lower = signals.get("bb_lower", 0)
        if bb_upper > 0 and close < bb_lower:
            score += 15  # At lower band - BUY
        elif bb_upper > 0 and close > bb_upper:
            score -= 15  # At upper band - SELL

        # Stochastic
        stoch_k = signals.get("stoch_k", 50)
        stoch_d = signals.get("stoch_d", 50)
        if stoch_k < 20:
            score += 10
        elif stoch_k > 80:
            score -= 10

        # Volume confirmation
        volume_ratio = signals.get("volume_ratio", 1)
        if volume_ratio > 1.5:
            score += 5 if score > 0 else -5

        return max(-100, min(100, score))

    def _calculate_confidence(self, signals):
        """Calculate confidence level (0-100)"""
        confidence = 50  # Base confidence

        # More indicators aligned = higher confidence
        rsi = signals.get("rsi", 50)
        macd_hist = signals.get("macd_hist", 0)
        sma_20 = signals.get("sma_20", 0)
        close = signals.get("close", 0)

        aligned_bullish = 0
        aligned_bearish = 0

        if rsi < 40:
            aligned_bullish += 1
        elif rsi > 60:
            aligned_bearish += 1

        if macd_hist > 0:
            aligned_bullish += 1
        else:
            aligned_bearish += 1

        if close > sma_20:
            aligned_bullish += 1
        else:
            aligned_bearish += 1

        alignment = abs(aligned_bullish - aligned_bearish)
        confidence += alignment * 10

        return max(0, min(100, confidence))

    def _determine_action(self, score, confidence, signals):
        """Determine action based on score and confidence"""
        if confidence < self.min_confidence:
            return "HOLD"

        if score >= 30 and confidence >= 60:
            return "BUY"
        elif score <= -30 and confidence >= 60:
            return "SELL"
        elif score >= 15:
            return "BUY"
        elif score <= -15:
            return "SELL"

        return "HOLD"

    def _generate_reason(self, action, signals):
        """Generate human-readable reason for signal"""
        reasons = []

        rsi = signals.get("rsi", 50)
        if rsi < 30:
            reasons.append("RSI oversold")
        elif rsi > 70:
            reasons.append("RSI overbought")

        macd_hist = signals.get("macd_hist", 0)
        if macd_hist > 0:
            reasons.append("MACD bullish")
        else:
            reasons.append("MACD bearish")

        stoch_k = signals.get("stoch_k", 50)
        if stoch_k < 20:
            reasons.append("Stochastic oversold")
        elif stoch_k > 80:
            reasons.append("Stochastic overbought")

        if not reasons:
            reasons.append("Technical neutral")

        return f"{action}: {', '.join(reasons)}"

    def _calculate_levels(self, ltp, signals, action):
        """Calculate target and stop-loss levels"""
        atr = signals.get("atr", 0)
        bb_upper = signals.get("bb_upper", 0)
        bb_lower = signals.get("bb_lower", 0)

        if action == "BUY":
            target = ltp + (atr * 2) if atr > 0 else ltp * 1.02
            sl = ltp - (atr * 1.5) if atr > 0 else ltp * 0.98
        elif action == "SELL":
            target = ltp - (atr * 2) if atr > 0 else ltp * 0.98
            sl = ltp + (atr * 1.5) if atr > 0 else ltp * 1.02
        else:
            target = ltp
            sl = ltp

        return round(target, 2), round(sl, 2)