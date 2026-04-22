#!/usr/bin/env python3
"""
Standalone Backtester Script
Run historical performance analysis on trading signals
"""

import argparse
import sys
import os
from datetime import datetime
from logzero import logger, logfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'angel_agent'))

from angel_agent.modules.database import Database
from angel_agent.modules.backtester import Backtester

os.makedirs("logs", exist_ok=True)
logfile(f"logs/backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")


def main():
    parser = argparse.ArgumentParser(description="Backtest trading signals on historical data")
    parser.add_argument("--symbol", default="RELIANCE", help="Stock symbol (default: RELIANCE)")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD), default: 30 days ago")
    parser.add_argument("--end", help="End date (YYYY-MM-DD), default: today")
    parser.add_argument("--capital", type=float, default=10000, help="Initial capital (default: 10000)")
    parser.add_argument("--save", action="store_true", help="Save report to CSV")

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Backtester - {args.symbol}")
    print(f"{'='*60}\n")

    try:
        db = Database()
        backtester = Backtester(args.symbol, db, args.start, args.end)

        print(f"Running backtest from {backtester.start_date} to {backtester.end_date}...")
        metrics = backtester.run_backtest(initial_capital=args.capital)

        if metrics:
            print("\n" + backtester.format_backtest_report())

            if args.save:
                backtester.save_report()
                print(f"Report saved to backtest_reports/backtest_results.csv")
        else:
            print("Backtest failed or no data available")

        db.close()

    except Exception as e:
        logger.error(f"Backtest error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
