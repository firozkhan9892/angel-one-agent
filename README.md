# Angel One Trading Agent - Advanced Features

A production-grade 24/7 automated trading signal generator for Angel One Indian stock market with AI predictions, portfolio management, risk controls, and live dashboard.

## Features

### Core Signal Generation
- **Real-time Technical Indicators**: RSI, MACD, EMA, VWAP, Bollinger Bands
- **Confluence Scoring**: Multi-indicator analysis (-100 to +100 scale)
- **BUY/SELL/HOLD Signals**: Generated every 5 minutes during market hours
- **Telegram Alerts**: Instant notifications with signal details
- **Company News Integration**: Real order announcements from Finnhub API

### Advanced Features (Phase 1-5)

#### Phase 1: Database Layer ✅
- **SQLite Persistence**: Signals, positions, metrics, OHLCV history
- **Signal History**: Track all generated signals with entry/exit prices
- **Position Tracking**: Open/closed positions with P&L calculation
- **Performance Metrics**: Daily win rate, drawdown, ROI

#### Phase 2: Portfolio Manager ✅
- **Multi-Position Tracking**: Monitor multiple open positions
- **P&L Calculation**: Real-time profit/loss tracking
- **Portfolio Summary**: Total P&L, win rate, signal count
- **Telegram Commands**: `/portfolio`, `/position SYMBOL`

#### Phase 3: Risk Manager ✅
- **Dynamic Position Sizing**: Kelly Criterion-based sizing
- **Drawdown Tracking**: Current and max drawdown monitoring
- **Trading Pause Logic**: Auto-pause if drawdown exceeds threshold
- **Risk Alerts**: Telegram notifications for risk events

#### Phase 4: Backtester ✅
- **Historical Simulation**: Replay signals on past data
- **Performance Metrics**: Win rate, ROI, Sharpe ratio, max drawdown
- **Report Generation**: CSV export of backtest results
- **Standalone Script**: `python backtest.py --symbol RELIANCE --start 2024-01-01`

#### Phase 5: Live Dashboard ✅
- **Real-time Web UI**: Flask-based monitoring dashboard
- **Signal Stream**: Last 20 signals with details
- **Portfolio View**: Open positions, P&L, win rate
- **Risk Metrics**: Drawdown, account balance, trading status
- **Performance Charts**: 30-day metrics and trends
- **Auto-refresh**: Updates every 5 seconds

## Installation

```bash
# Clone repository
git clone <repo-url>
cd angel_agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

### .env File
```env
# Angel One Credentials
API_KEY=your_api_key
CLIENT_ID=your_client_id
PASSWORD=your_password
TOTP_SECRET=your_totp_secret

# Trading Settings
SYMBOL=RELIANCE
EXCHANGE=NSE
INTERVAL=FIVE_MINUTE
TRADE_QUANTITY=1

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Finnhub News API
FINNHUB_API_KEY=your_finnhub_key

# Risk Management
ACCOUNT_SIZE=10000
RISK_PER_TRADE=0.02
MAX_DRAWDOWN_THRESHOLD=0.15

# Dashboard
PORT=5000
```

## Usage

### Run Main Agent
```bash
python agent.py --symbol RELIANCE --interval FIVE_MINUTE
```

### Run Backtester
```bash
# Backtest last 30 days
python backtest.py --symbol RELIANCE

# Backtest specific date range
python backtest.py --symbol RELIANCE --start 2024-01-01 --end 2024-12-31

# Save report to CSV
python backtest.py --symbol RELIANCE --save
```

### Run Dashboard
```bash
cd dashboard
python app.py
# Access at http://localhost:5000
```

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/status` | Market open/closed status |
| `/help` | Show available commands |
| `/signals` | Today's signal count |
| `/latest` | Latest signal details |
| `/portfolio` | Portfolio summary with P&L |
| `/position SYMBOL` | Specific position details |

## Database Schema

### signals
- id, timestamp, symbol, ltp, action, score, confidence, target, sl, entry_price, exit_price, pnl, status

### positions
- id, symbol, quantity, entry_price, entry_time, exit_price, exit_time, pnl, status

### metrics
- id, date, total_signals, winning_signals, losing_signals, win_rate, total_pnl, max_drawdown

### ohlcv_history
- id, symbol, timestamp, open, high, low, close, volume

## API Endpoints (Dashboard)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/signals` | GET | Recent signals (limit 20) |
| `/api/portfolio` | GET | Portfolio summary |
| `/api/positions` | GET | Open positions |
| `/api/risk` | GET | Risk metrics |
| `/api/metrics` | GET | Performance metrics (30 days) |
| `/api/health` | GET | Health check |

## File Structure

```
angel_agent/
├── agent.py                    # Main orchestrator
├── backtest.py                 # Standalone backtester
├── requirements.txt            # Dependencies
├── .env                        # Configuration
├── modules/
│   ├── angel_connector.py      # Angel One API integration
│   ├── indicators.py           # Technical indicators
│   ├── signal_generator.py     # Signal generation
│   ├── telegram_notifier.py    # Telegram alerts
│   ├── telegram_commands.py    # Telegram commands
│   ├── news_scraper.py         # Finnhub news integration
│   ├── database.py             # SQLite manager
│   ├── portfolio_manager.py    # Position tracking
│   ├── risk_manager.py         # Risk management
│   └── backtester.py           # Historical simulation
├── dashboard/
│   ├── app.py                  # Flask backend
│   ├── templates/
│   │   └── index.html          # Dashboard UI
│   └── static/
│       ├── style.css           # Styling
│       └── script.js           # Real-time updates
├── data/
│   └── trading_agent.db        # SQLite database
├── logs/
│   └── agent_YYYYMMDD.log      # Daily logs
└── output/
    └── signals_log.csv         # Signal history (CSV)
```

## Key Metrics

### Portfolio Metrics
- **Open Positions**: Number of active trades
- **Open P&L**: Unrealized profit/loss
- **Closed P&L**: Realized profit/loss
- **Total P&L**: Sum of open + closed P&L
- **Win Rate**: % of winning signals
- **Total Signals**: Cumulative signal count

### Risk Metrics
- **Current Drawdown**: Current loss from peak
- **Max Drawdown Threshold**: Configured limit (default 15%)
- **Account Balance**: Current account value
- **Peak Balance**: Highest account value
- **Risk Per Trade**: % of account risked per trade (default 2%)

### Performance Metrics
- **ROI**: Return on investment %
- **Sharpe Ratio**: Risk-adjusted returns
- **Win Rate**: % of profitable trades
- **Avg Win**: Average profit per winning trade
- **Max Drawdown**: Largest peak-to-trough decline

## Deployment on Render

### Procfile
```
web: cd dashboard && python app.py
worker: python angel_agent/agent.py
```

### Environment Variables
Set all `.env` variables in Render dashboard settings.

### Keep-Alive (Free Tier)
Use UptimeRobot to ping every 5 minutes:
```
https://your-app.onrender.com/api/health
```

## Important Notes

⚠️ **No Auto-Trading**: All signals are informational only. Manual execution required.

⚠️ **Paper Trading**: Test thoroughly before live trading.

⚠️ **Risk Management**: Always set appropriate position sizes and stop losses.

⚠️ **Market Hours**: Agent only trades 9:15 AM - 3:30 PM IST (Mon-Fri).

## Troubleshooting

### Database Errors
- Check `data/` directory exists and is writable
- Verify SQLite is installed: `python -c "import sqlite3"`

### Telegram Not Working
- Verify bot token and chat ID in `.env`
- Test with: `python -c "from modules.telegram_notifier import TelegramNotifier; TelegramNotifier().send_error('Test')"`

### Dashboard Not Loading
- Check Flask is running: `python dashboard/app.py`
- Verify port 5000 is not in use
- Check browser console for API errors

### Signals Not Generating
- Verify Angel One credentials in `.env`
- Check market hours (9:15 AM - 3:30 PM IST)
- Review logs: `tail -f logs/agent_*.log`

## Support

For issues, check:
1. Logs in `logs/` directory
2. Database integrity: `sqlite3 data/trading_agent.db ".tables"`
3. Telegram connectivity
4. Angel One API status

## License

Proprietary - Angel One Trading Agent v1.0
