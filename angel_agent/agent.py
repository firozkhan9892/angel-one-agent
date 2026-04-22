"""
Angel One Trading Agent - Simple Version
Generates trading signals and sends Telegram alerts
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from logzero import logger, logfile

# Setup logging
os.makedirs("logs", exist_ok=True)
logfile(f"logs/agent_{datetime.now().strftime('%Y%m%d')}.log", maxBytes=5_000_000, backupCount=3)

load_dotenv()

# Import modules
from modules.angel_connector import AngelConnector
from modules.indicators import IndicatorEngine
from modules.signal_generator import SignalGenerator
from modules.telegram_notifier import TelegramNotifier
from modules.database import Database
from modules.portfolio_manager import PortfolioManager
from modules.risk_manager import RiskManager

MARKET_OPEN = (9, 15)
MARKET_CLOSE = (15, 30)

def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    t = (now.hour, now.minute)
    return MARKET_OPEN <= t <= MARKET_CLOSE

def main():
    logger.info("🚀 Angel One Trading Agent Started")

    connector = AngelConnector()
    engine = IndicatorEngine()
    generator = SignalGenerator()
    telegram = TelegramNotifier()
    db = Database()
    portfolio = PortfolioManager(db)
    risk_mgr = RiskManager()

    if not connector.login():
        logger.error("❌ Login failed")
        telegram.send_error("Login failed")
        return

    logger.info("✅ Login successful")
    telegram.send_startup(os.getenv("SYMBOL", "RELIANCE"), os.getenv("INTERVAL", "FIVE_MINUTE"))

    scan_count = 0

    while True:
        if not is_market_open():
            logger.info("🕐 Market closed, waiting...")
            time.sleep(300)
            continue

        try:
            scan_count += 1
            logger.info(f"🔍 Scan #{scan_count}")

            symbol = os.getenv("SYMBOL", "RELIANCE")
            token = os.getenv("SYMBOL_TOKEN", "2885")
            exchange = os.getenv("EXCHANGE", "NSE")
            interval = os.getenv("INTERVAL", "FIVE_MINUTE")

            # Fetch data
            df = connector.get_historical_data(token, exchange, interval, days=5)
            if not df:
                logger.warning("⚠️ No data received")
                time.sleep(60)
                continue

            # Compute indicators
            df = IndicatorEngine.compute_all(df)

            # Generate signal
            signal = generator.generate(df)

            # Check risk
            if not risk_mgr.should_trade():
                logger.warning("⚠️ Trading paused - drawdown threshold exceeded")
                telegram.send_error("Trading paused: Drawdown threshold exceeded")
                time.sleep(300)
                continue

            # Save to database
            db.save_signal(symbol, signal.ltp, signal.action, signal.score, signal.confidence, signal.target, signal.sl)

            # Handle positions
            if signal.action == "BUY":
                qty = risk_mgr.calculate_position_size(signal.ltp, signal.sl)
                portfolio.open_position(symbol, qty, signal.ltp, signal)
            elif signal.action == "SELL":
                result = portfolio.close_position(symbol, signal.ltp)
                if result:
                    risk_mgr.update_balance(result.get('pnl', 0))

            # Send alert
            telegram.send_signal(signal)
            logger.info(f"✅ Signal: {signal.action} @ {signal.ltp}")

            # Wait for next candle
            sleep_time = int(os.getenv("INTERVAL_SLEEP", "300"))
            logger.info(f"⏳ Next scan in {sleep_time//60} minutes")
            time.sleep(sleep_time)

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            telegram.send_error(f"Error: {str(e)}")
            time.sleep(60)

    connector.logout()
    db.close()

if __name__ == "__main__":
    main()
