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
from modules.telegram_interactive_commands import TelegramInteractiveCommands
from modules.database import Database
from modules.portfolio_manager import PortfolioManager
from modules.risk_manager import RiskManager
from modules.price_predictor import PricePredictor
from modules.backtester import Backtester
from modules.news_integrator import NewsIntegrator
from modules.multi_symbol_manager import MultiSymbolManager
from modules.advanced_risk_controls import AdvancedRiskControls
from modules.performance_dashboard import PerformanceDashboard
from modules.watchlist_monitor import WatchlistMonitor
from modules.sentiment_analyzer import SentimentAnalyzer

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
    interactive_cmd = TelegramInteractiveCommands(os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID"))
    db = Database()
    portfolio = PortfolioManager(db)
    risk_mgr = RiskManager()
    predictor = PricePredictor(lookback=20)
    backtester = Backtester()
    news = NewsIntegrator(os.getenv("FINNHUB_API_KEY", ""))
    symbol_mgr = MultiSymbolManager()
    advanced_risk = AdvancedRiskControls(int(os.getenv("ACCOUNT_SIZE", "10000")))
    dashboard = PerformanceDashboard()
    watchlist = WatchlistMonitor()
    sentiment = SentimentAnalyzer(os.getenv("FINNHUB_API_KEY", ""))

    if not connector.login():
        logger.error("Login failed")
        telegram.send_error("Login failed")
        return

    logger.info("Login successful")
    active_symbols = symbol_mgr.get_active_symbols()
    telegram.send_startup(", ".join(active_symbols), os.getenv("INTERVAL", "FIVE_MINUTE"))

    scan_count = 0
    last_news_check = 0
    last_dashboard_check = 0
    update_offset = 0

    while True:
        try:
            # Check for Telegram updates (commands and confirmations) - ALWAYS, even outside market hours
            updates = interactive_cmd.get_updates(update_offset, timeout=5)
            if updates:
                logger.info(f"Received {len(updates)} Telegram updates")

            for update in updates:
                update_offset = update['update_id'] + 1

                # Handle trade confirmations
                if 'callback_query' in update:
                    query = update['callback_query']
                    logger.info(f"Callback query: {query['data']}")
                    approved_trade = cmd_handler.handle_callback_query(query['id'], query['data'], telegram)
                    if approved_trade:
                        logger.info(f"Trade approved: {approved_trade['symbol']} {approved_trade['action']}")

                # Handle text commands
                elif 'message' in update:
                    message = update['message']
                    if 'text' in message:
                        logger.info(f"Text message received: {message['text']}")
                        reply = interactive_cmd.process_message(message, portfolio, dashboard, watchlist, sentiment, symbol_mgr)
                        if reply:
                            logger.info(f"Sending reply: {reply[:100]}")
                            interactive_cmd.send_reply(reply, message['message_id'])
                            logger.info(f"Command processed: {message['text']}")
                        else:
                            logger.warning(f"No reply generated for: {message['text']}")

        except Exception as e:
            logger.error(f"Error processing Telegram updates: {e}", exc_info=True)

        # Skip trading logic if market is closed
        if not is_market_open():
            logger.info("Market closed, waiting...")
            time.sleep(300)
            continue

        try:

            scan_count += 1
            logger.info(f"Scan #{scan_count}")

            # Process each active symbol
            for symbol in active_symbols:
                try:
                    config = symbol_mgr.get_symbol_config(symbol)
                    token = config['token']
                    exchange = config['exchange']
                    interval = os.getenv("INTERVAL", "FIVE_MINUTE")

                    # Fetch data
                    df = connector.get_historical_data(token, exchange, interval, days=5)
                    if not df:
                        logger.warning(f"No data for {symbol}")
                        continue

                    # Compute indicators
                    df = IndicatorEngine.compute_all(df)

                    # Get LSTM prediction
                    lstm_score = predictor.get_prediction_score(df)

                    # Get sentiment adjustment
                    sentiment_adjustment = sentiment.get_sentiment_score_adjustment(symbol)

                    # Generate signal with LSTM + sentiment boost
                    signal = generator.generate(df)
                    signal.score = min(100, max(-100, signal.score + lstm_score + sentiment_adjustment))

                    # Filter by sentiment if needed
                    if not sentiment.filter_signal_by_sentiment(signal, symbol):
                        logger.info(f"Signal filtered by sentiment: {symbol}")
                        continue

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
                        qty = advanced_risk.calculate_position_size_kelly(0.55, 100, 50)
                        if qty == 0:
                            qty = risk_mgr.calculate_position_size(signal.ltp, signal.sl)

                        telegram.send_trade_confirmation(symbol, signal.action, int(qty), signal.ltp, signal.target, signal.sl)
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
                            logger.info(f"Trade not confirmed: {signal.action} {symbol}")
                            telegram.send_message(f"Trade not confirmed: {signal.action} {symbol}")
                    else:
                        telegram.send_signal(signal)

                    logger.info(f"Signal: {signal.action} @ {signal.ltp} for {symbol}")

                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    continue

            # Check news every 30 minutes
            if scan_count - last_news_check >= 6:
                for symbol in active_symbols:
                    news_alert = news.get_news_alert(symbol, os.getenv("FINNHUB_API_KEY", ""))
                    if news_alert:
                        telegram.send_message(news_alert)
                last_news_check = scan_count

            # Send performance dashboard every 2 hours
            if scan_count - last_dashboard_check >= 24:
                dashboard_report = dashboard.format_dashboard_report(days=7)
                telegram.send_message(dashboard_report)
                last_dashboard_check = scan_count

            # Send watchlist summary every 4 hours
            if scan_count % 48 == 0:
                watchlist_report = watchlist.format_watchlist_report()
                telegram.send_message(watchlist_report)

            # Send sentiment report every 6 hours
            if scan_count % 72 == 0:
                sentiment_report = sentiment.get_sentiment_report(active_symbols)
                telegram.send_message(sentiment_report)

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
