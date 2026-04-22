"""
AI Sentiment Analysis - Analyze news sentiment to filter signals
"""

import requests
from logzero import logger


class SentimentAnalyzer:
    """Analyze sentiment from news and social signals"""

    def __init__(self, finnhub_api_key=""):
        self.finnhub_api_key = finnhub_api_key
        self.base_url = "https://finnhub.io/api/v1"

    def analyze_headline_sentiment(self, headline):
        """Analyze sentiment of a single headline"""
        positive_words = [
            'surge', 'gain', 'rally', 'jump', 'soar', 'bull', 'profit', 'growth',
            'beat', 'strong', 'outperform', 'upgrade', 'bullish', 'buy', 'positive',
            'excellent', 'record', 'breakthrough', 'success', 'momentum'
        ]

        negative_words = [
            'fall', 'drop', 'crash', 'plunge', 'bear', 'loss', 'decline', 'miss',
            'weak', 'down', 'underperform', 'downgrade', 'bearish', 'sell', 'negative',
            'poor', 'warning', 'risk', 'concern', 'weakness'
        ]

        headline_lower = headline.lower()
        positive_count = sum(1 for word in positive_words if word in headline_lower)
        negative_count = sum(1 for word in negative_words if word in headline_lower)

        if positive_count > negative_count:
            return 'POSITIVE', positive_count / (positive_count + negative_count + 1)
        elif negative_count > positive_count:
            return 'NEGATIVE', negative_count / (positive_count + negative_count + 1)
        else:
            return 'NEUTRAL', 0.5

    def get_news_sentiment(self, symbol, days=7):
        """Get overall sentiment from recent news"""
        try:
            from datetime import datetime, timedelta

            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')

            url = f"{self.base_url}/company-news"
            params = {
                'symbol': symbol,
                'from': from_date,
                'to': to_date,
                'token': self.finnhub_api_key
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            news_list = response.json()
            if not isinstance(news_list, list) or not news_list:
                return 'NEUTRAL', 0.5

            sentiments = []
            for news in news_list[:10]:
                headline = news.get('headline', '')
                sentiment, score = self.analyze_headline_sentiment(headline)
                sentiments.append((sentiment, score))

            positive_count = sum(1 for s, _ in sentiments if s == 'POSITIVE')
            negative_count = sum(1 for s, _ in sentiments if s == 'NEGATIVE')
            avg_score = sum(s for _, s in sentiments) / len(sentiments)

            if positive_count > negative_count:
                return 'POSITIVE', avg_score
            elif negative_count > positive_count:
                return 'NEGATIVE', avg_score
            else:
                return 'NEUTRAL', avg_score

        except Exception as e:
            logger.error(f"Error getting news sentiment: {e}")
            return 'NEUTRAL', 0.5

    def filter_signal_by_sentiment(self, signal, symbol, min_sentiment_score=0.6):
        """Filter signal based on sentiment analysis"""
        sentiment, score = self.get_news_sentiment(symbol)

        if signal.action == "BUY":
            if sentiment == "NEGATIVE" and score > min_sentiment_score:
                logger.warning(f"BUY signal filtered: Negative sentiment for {symbol}")
                return False
        elif signal.action == "SELL":
            if sentiment == "POSITIVE" and score > min_sentiment_score:
                logger.warning(f"SELL signal filtered: Positive sentiment for {symbol}")
                return False

        return True

    def get_sentiment_score_adjustment(self, symbol):
        """Get sentiment-based score adjustment for signals"""
        sentiment, score = self.get_news_sentiment(symbol)

        if sentiment == "POSITIVE":
            return int(20 * score)
        elif sentiment == "NEGATIVE":
            return int(-20 * score)
        else:
            return 0

    def get_sentiment_report(self, symbols):
        """Get sentiment report for multiple symbols"""
        report = "Sentiment Analysis Report\n\n"

        for symbol in symbols:
            sentiment, score = self.get_news_sentiment(symbol)
            report += f"{symbol}: {sentiment} ({score:.2f})\n"

        return report

    def analyze_multiple_symbols(self, symbols):
        """Analyze sentiment for multiple symbols"""
        results = {}

        for symbol in symbols:
            sentiment, score = self.get_news_sentiment(symbol)
            results[symbol] = {
                'sentiment': sentiment,
                'score': score,
                'adjustment': self.get_sentiment_score_adjustment(symbol)
            }

        return results
