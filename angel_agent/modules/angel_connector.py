"""
Angel One SmartAPI Connector
Handles login and data fetching from Angel One
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from smartapi import SmartConnect
from logzero import logger

class AngelConnector:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.client_id = os.getenv("CLIENT_ID")
        self.password = os.getenv("PASSWORD")
        self.totp_secret = os.getenv("TOTP_SECRET")
        self.obj = None
        self.feed_token = None

    def login(self):
        """Login to Angel One SmartAPI"""
        try:
            import pyotp
            self.obj = SmartConnect(api_key=self.api_key)
            token = pyotp.TOTP(self.totp_secret).now()
            data = self.obj.generateSession(self.client_id, self.password, token)

            if data.get("status"):
                self.feed_token = self.obj.getfeedToken()
                logger.info("Login successful")
                return True
            else:
                logger.error(f"Login failed: {data.get('message')}")
                return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def get_historical_data(self, token, exchange, interval, days=5):
        """Fetch historical candle data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            params = {
                "exchange": exchange,
                "symboltoken": token,
                "interval": interval,
                "fromdate": start_date.strftime("%Y-%m-%d %H:%M"),
                "todate": end_date.strftime("%Y-%m-%d %H:%M")
            }

            data = self.obj.getCandleData(params)

            if data.get("status"):
                candles = data["data"]
                df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df.set_index("timestamp", inplace=True)
                df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
                return df
            else:
                logger.warning(f"No data: {data.get('message')}")
                return None
        except Exception as e:
            logger.error(f"Historical data error: {e}")
            return None

    def logout(self):
        """Logout from Angel One"""
        try:
            if self.obj:
                self.obj.terminateSession(self.client_id)
                logger.info("Logged out")
        except Exception as e:
            logger.error(f"Logout error: {e}")