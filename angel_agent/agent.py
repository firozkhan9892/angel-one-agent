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
from modules.telegram_commands import TelegramCommandHandler
from modules.database import Database
from modules.portfolio_manager import PortfolioManager
from modules.risk_manager import RiskManager
from modules.price_predictor import PricePredictor
from modules.backtester import Backtester
from modules.news_integrator import NewsIntegrator

MARKET_OPEN = (9, 15)
MARKET_CLOSE = (15, 30)

def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    t = (now.hour, now.minute)
    return MARKET_OPEN <= t <= MARKET_CLOSE

def main():
    logger.info("Angel One Trading Agent Started")

    connector = AngelConnector()
    engine = IndicatorEngine()
    generator = SignalGenerator()
    telegram = TelegramNotifier(os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID"))
    cmd_handler = TelegramCommandHandler(os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID"))
    db = Database()
    portfolio = PortfolioManager(db)
    risk_mgr = RiskManager()
    predictor = PricePredictor(lookback=20)
    backtester = Backtester()
    news = NewsIntegrator(os.getenv("FINNHUB_API_KEY", ""))

    if not connector.login():
        logger.error("Login failed")
        telegram.send_error("Login failed")
        return

    logger.info("Login successful")
    telegram.send_startup(os.getenv("SYMBOL", "RELIANCE"), os.getenv("INTERVAL", "FIVE_MINUTE"))

    scan_count = 0
    last_news_check = 0
    update_offset = 0

    while True:
        if not is_market_open():
            logger.info("Market closed, waiting...")
            time.sleep(300)
            continue

        try:
            # Check for trade confirmations
            updates = cmd_handler.get_updates(update_offset)
            for update in updates:
                update_offset = update['update_id'] + 1
                if 'callback_query' in update:
                    query = update['callback_query']
                    approved_trade = cmd_handler.handle_callback_query(query['id'], query['data'], telegram)
                    if approved_trade:
                        logger.info(f"Trade approved: {approved_trade['symbol']} {approved_trade['action']}")

            scan_count += 1
            logger.info(f"Scan #{scan_count}")

            symbol = os.getenv("SYMBOL", "RELIANCE")
            token = os.getenv("SYMBOL_TOKEN", "2885")
            exchange = os.getenv("EXCHANGE", "NSE")
            interval = os.getenv("INTERVAL", "FIVE_MINUTE")

            # Fetch data
            df = connector.get_historical_data(token, exchange, interval, days=5)
            if not df:
                logger.warning("No data received")
                time.sleep(60)
                continue

            # Compute indicators
            df = IndicatorEngine.compute_all(df)

            # Get LSTM prediction
            lstm_score = predictor.get_prediction_score(df)
            logger.info(f"LSTM prediction score: {lstm_score}")

            # Generate signal with LSTM boost
            signal = generator.generate(df)
            signal.score = min(100, max(-100, signal.score + lstm_score))

            # Check risk
            if not risk_mgr.should_trade():
                logger.warning("Trading paused - drawdown threshold exceeded")
                telegram.send_error("Trading paused: Drawdown threshold exceeded")
                time.sleep(300)
                continue

            # Save to database
            db.save_signal(symbol, signal.ltp, signal.action, signal.score, signal.confidence, signal.target, signal.sl)

            # Request trade confirmation before executing
            if signal.action in ["BUY", "SELL"]:
                qty = risk_mgr.calculate_position_size(signal.ltp, signal.sl)
                telegram.send_trade_confirmation(symbol, signal.action, qty, signal.ltp, signal.target, signal.sl)
                logger.info(f"Confirmation requested for {signal.action} {symbol}")
                time.sleep(30)

                # Check if trade was approved
                approved = cmd_handler.get_approved_trade()
                if approved:
                    if signal.action == "BUY":
                        portfolio.open_position(symbol, approved['qty'], approved['price'], signal)
                        telegram.send_position_update(symbol, "BUY", approved['qty'], approved['price'])
                    elif signal.action == "SELL":
                        result = portfolio.close_position(symbol, approved['price'])
                        if result:
                            risk_mgr.update_balance(result.get('pnl', 0))
                            telegram.send_position_update(symbol, "SELL", approved['qty'], approved['price'], result.get('pnl', 0))
                else:
                    logger.info(f"Trade rejected or not confirmed: {signal.action}")
                    telegram.send_message(f"Trade not confirmed: {signal.action} {symbol}")
            else:
                telegram.send_signal(signal)

            logger.info(f"Signal: {signal.action} @ {signal.ltp}")

            # Check news every 30 minutes
            if scan_count - last_news_check >= 6:
                news_alert = news.get_news_alert(symbol, os.getenv("FINNHUB_API_KEY", ""))
                if news_alert:
                    telegram.send_message(news_alert)
                last_news_check = scan_count

            # Send performance metrics every hour
            if scan_count % 12 == 0:
                metrics = backtester.get_portfolio_performance(days=7)
                perf_msg = f"7-Day Performance:\nSignals: {metrics['total_signals']}\nWin Rate: {metrics['win_rate']}%\nP&L: {metrics['total_pnl']}"
                telegram.send_message(perf_msg)

            # Wait for next candle
            sleep_time = int(os.getenv("INTERVAL_SLEEP", "300"))
            logger.info(f"Next scan in {sleep_time//60} minutes")
            time.sleep(sleep_time)

        except Exception as e:
            logger.error(f"Error: {e}")
            telegram.send_error(f"Error: {str(e)}")
            time.sleep(60)

    connector.logout()
    db.close()

if __name__ == "__main__":
    main()
