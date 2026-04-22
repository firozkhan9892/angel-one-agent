"""
News Integration - Fetch company news and market sentiment
"""

import requests
from datetime import datetime, timedelta
from logzero import logger


class NewsIntegrator:
    """Fetch and analyze company news from Finnhub API"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"

    def get_company_news(self, symbol, days=7):
        """Fetch latest company news"""
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')

            url = f"{self.base_url}/company-news"
            params = {
                'symbol': symbol,
                'from': from_date,
                'to': to_date,
                'token': self.api_key
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            news_list = response.json()
            if not isinstance(news_list, list):
                return []

            # Format news
            formatted_news = []
            for news in news_list[:5]:  # Top 5 news
                formatted_news.append({
                    'headline': news.get('headline', ''),
                    'summary': news.get('summary', ''),
                    'source': news.get('source', ''),
                    'url': news.get('url', ''),
                    'datetime': news.get('datetime', 0)
                })

            return formatted_news

        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

    def get_sentiment_score(self, news_list):
        """
        Analyze sentiment from news headlines
        Returns: sentiment_score (-1 to +1)
        """
        if not news_list:
            return 0

        positive_keywords = ['surge', 'gain', 'rally', 'jump', 'soar', 'bull', 'profit', 'growth', 'beat', 'strong']
        negative_keywords = ['fall', 'drop', 'crash', 'plunge', 'bear', 'loss', 'decline', 'miss', 'weak', 'down']

        sentiment_sum = 0
        for news in news_list:
            headline = news.get('headline', '').lower()

            for keyword in positive_keywords:
                if keyword in headline:
                    sentiment_sum += 1

            for keyword in negative_keywords:
                if keyword in headline:
                    sentiment_sum -= 1

        # Normalize to -1 to +1
        max_possible = len(news_list) * len(positive_keywords)
        if max_possible > 0:
            sentiment = sentiment_sum / max_possible
            return max(-1, min(1, sentiment))

        return 0

    def get_news_alert(self, symbol, api_key):
        """Get formatted news alert for Telegram"""
        try:
            news_list = self.get_company_news(symbol)
            if not news_list:
                return None

            top_news = news_list[0]
            sentiment = self.get_sentiment_score(news_list)

            sentiment_emoji = "UP" if sentiment > 0.3 else "DOWN" if sentiment < -0.3 else "NEUTRAL"

            alert = f"NEWS: {symbol}\n"
            alert += f"Headline: {top_news['headline'][:80]}\n"
            alert += f"Source: {top_news['source']}\n"
            alert += f"Sentiment: {sentiment_emoji}"

            return alert

        except Exception as e:
            logger.error(f"Error generating news alert: {e}")
            return None
