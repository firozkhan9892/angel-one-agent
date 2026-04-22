# Quick Start Guide

## 5-Minute Setup

### 1. Get Credentials
- **Angel One**: https://www.angelbroking.com/ (SmartAPI credentials)
- **Telegram**: Create bot via @BotFather on Telegram
- **Finnhub**: Free API key from https://finnhub.io

### 2. Clone & Install
```bash
git clone <repo-url>
cd angel_agent
pip install -r requirements.txt
```

### 3. Configure
```bash
# Edit .env with your credentials
nano .env
```

### 4. Run
```bash
# Terminal 1: Agent
python agent.py

# Terminal 2: Dashboard
cd dashboard && python app.py
```

### 5. Access
- Dashboard: http://localhost:5000
- Telegram: Receive signal alerts

## What Each Component Does

| Component | Purpose | Runs |
|-----------|---------|------|
| **agent.py** | Generates signals, sends alerts | Continuous (market hours) |
| **dashboard/app.py** | Web UI for monitoring | Continuous |
| **backtest.py** | Historical analysis | On-demand |
| **database.py** | Stores all data | Background |

## First Run Checklist

- [ ] Agent connects to Angel One API
- [ ] First signal generated (check console)
- [ ] Telegram alert received
- [ ] Dashboard loads at http://localhost:5000
- [ ] Portfolio shows open positions
- [ ] Risk metrics display correctly

## Common Commands

```bash
# Run agent for specific symbol
python agent.py --symbol INFY --interval FIVE_MINUTE

# Backtest last 30 days
python backtest.py --symbol RELIANCE

# Backtest with date range
python backtest.py --symbol RELIANCE --start 2024-01-01 --end 2024-12-31

# Run dashboard on custom port
cd dashboard && PORT=8000 python app.py
```

## Telegram Commands

Send these to your Telegram bot:
- `/status` - Market status
- `/portfolio` - Your positions
- `/help` - All commands

## Dashboard Tabs

1. **Signals** - Last 20 signals generated
2. **Portfolio** - Open positions, P&L, win rate
3. **Risk** - Drawdown, account balance, trading status
4. **Metrics** - 30-day performance history

## Troubleshooting

**Agent won't start**
```bash
# Check credentials
python -c "from modules.angel_connector import AngelConnector; AngelConnector().login()"
```

**No signals generated**
- Check market hours (9:15 AM - 3:30 PM IST, Mon-Fri)
- Verify symbol token is correct
- Check logs: `tail -f logs/agent_*.log`

**Dashboard not loading**
```bash
# Check Flask is running
curl http://localhost:5000/api/health
```

**Telegram not working**
- Verify bot token in .env
- Verify chat ID is correct
- Test: `/help` command

## Next Steps

1. Run agent for 1 week
2. Review backtest results
3. Adjust risk parameters if needed
4. Deploy to Render (see DEPLOYMENT.md)
5. Monitor live performance

## Key Metrics to Watch

- **Win Rate**: Target > 50%
- **Drawdown**: Keep < 15%
- **Signals/Day**: Expect 5-10 signals
- **P&L**: Track daily and weekly trends

## Support

- Check README.md for detailed docs
- Review logs in `logs/` directory
- Test components individually
- See DEPLOYMENT.md for production setup
