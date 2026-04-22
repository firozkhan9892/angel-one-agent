# Testing Guide - Angel One Trading Agent

## Unit Tests

### Test Database Module
```python
# test_database.py
from angel_agent.modules.database import Database

def test_database_initialization():
    db = Database(":memory:")  # Use in-memory DB for testing
    assert db.conn is not None
    db.close()

def test_save_signal():
    db = Database(":memory:")
    signal_id = db.save_signal(
        symbol="RELIANCE",
        ltp=2500.0,
        action="BUY",
        score=75,
        confidence="HIGH",
        target=2600.0,
        sl=2400.0
    )
    assert signal_id is not None
    db.close()

def test_open_position():
    db = Database(":memory:")
    result = db.open_position("RELIANCE", 1, 2500.0)
    assert result is True
    db.close()

def test_close_position():
    db = Database(":memory:")
    db.open_position("RELIANCE", 1, 2500.0)
    result = db.close_position("RELIANCE", 2550.0, 50.0)
    assert result is True
    db.close()
```

### Test Portfolio Manager
```python
# test_portfolio.py
from angel_agent.modules.database import Database
from angel_agent.modules.portfolio_manager import PortfolioManager

def test_portfolio_summary():
    db = Database(":memory:")
    portfolio = PortfolioManager(db)
    
    # Open position
    portfolio.open_position("RELIANCE", 1, 2500.0, None)
    
    # Get summary
    summary = portfolio.get_portfolio_summary()
    assert summary['open_positions_count'] == 1
    db.close()

def test_close_position_pnl():
    db = Database(":memory:")
    portfolio = PortfolioManager(db)
    
    # Open and close
    portfolio.open_position("RELIANCE", 1, 2500.0, None)
    result = portfolio.close_position("RELIANCE", 2550.0)
    
    assert result['pnl'] == 50.0
    db.close()
```

### Test Risk Manager
```python
# test_risk.py
from angel_agent.modules.risk_manager import RiskManager

def test_position_sizing():
    risk_mgr = RiskManager(account_size=10000, risk_per_trade=0.02)
    qty = risk_mgr.calculate_position_size(entry_price=2500, sl_price=2400)
    assert qty > 0

def test_drawdown_calculation():
    risk_mgr = RiskManager(account_size=10000)
    risk_mgr.update_balance(-1000)  # Lose 1000
    dd_info = risk_mgr.get_current_drawdown()
    assert dd_info['current_drawdown_pct'] > 0

def test_should_trade():
    risk_mgr = RiskManager(account_size=10000, max_drawdown_threshold=0.15)
    risk_mgr.update_balance(-2000)  # 20% drawdown
    assert risk_mgr.should_trade() is False
```

## Integration Tests

### Test Signal Generation Flow
```python
# test_signal_flow.py
from angel_agent.modules.database import Database
from angel_agent.modules.portfolio_manager import PortfolioManager
from angel_agent.modules.risk_manager import RiskManager

def test_buy_signal_flow():
    db = Database(":memory:")
    portfolio = PortfolioManager(db)
    risk_mgr = RiskManager()
    
    # Simulate BUY signal
    signal_id = db.save_signal(
        symbol="RELIANCE",
        ltp=2500.0,
        action="BUY",
        score=80,
        confidence="HIGH",
        target=2600.0,
        sl=2400.0
    )
    
    # Calculate position size
    qty = risk_mgr.calculate_position_size(2500.0, 2400.0)
    
    # Open position
    portfolio.open_position("RELIANCE", qty, 2500.0, None)
    
    # Verify
    positions = portfolio.get_open_positions()
    assert len(positions) == 1
    db.close()

def test_sell_signal_flow():
    db = Database(":memory:")
    portfolio = PortfolioManager(db)
    risk_mgr = RiskManager()
    
    # Open position
    portfolio.open_position("RELIANCE", 1, 2500.0, None)
    
    # Simulate SELL signal
    db.save_signal(
        symbol="RELIANCE",
        ltp=2550.0,
        action="SELL",
        score=75,
        confidence="HIGH",
        target=2500.0,
        sl=2600.0
    )
    
    # Close position
    result = portfolio.close_position("RELIANCE", 2550.0)
    
    # Update balance
    risk_mgr.update_balance(result['pnl'])
    
    # Verify
    assert result['pnl'] == 50.0
    db.close()
```

## Manual Testing Checklist

### Agent Startup
- [ ] Agent connects to Angel One API
- [ ] Logs show "Login successful"
- [ ] Database initializes without errors
- [ ] First scan completes within 30 seconds

### Signal Generation
- [ ] Signals generated every 5 minutes (during market hours)
- [ ] Signal contains: symbol, LTP, action, score, confidence, target, SL
- [ ] Signals saved to database
- [ ] Signals saved to CSV
- [ ] Console displays signal box with formatting

### Telegram Integration
- [ ] Startup message received
- [ ] Signal alerts received within 1 minute
- [ ] `/status` command returns market status
- [ ] `/help` command shows all commands
- [ ] `/portfolio` shows open positions
- [ ] `/position SYMBOL` shows specific position

### Portfolio Tracking
- [ ] BUY signal opens position
- [ ] SELL signal closes position
- [ ] P&L calculated correctly
- [ ] Win rate updates after each trade
- [ ] Portfolio summary shows correct totals

### Risk Management
- [ ] Position size calculated based on risk
- [ ] Drawdown tracked correctly
- [ ] Trading pauses when drawdown exceeds threshold
- [ ] Risk alerts sent to Telegram

### Dashboard
- [ ] Dashboard loads at http://localhost:5000
- [ ] Signals tab shows recent signals
- [ ] Portfolio tab shows open positions
- [ ] Risk tab shows drawdown metrics
- [ ] Metrics tab shows 30-day history
- [ ] Auto-refresh works every 5 seconds
- [ ] Manual refresh button works

### Backtester
- [ ] Backtest runs without errors
- [ ] Metrics calculated correctly
- [ ] Report saved to CSV
- [ ] Results match manual calculation

## Performance Testing

### Load Testing
```bash
# Test dashboard with concurrent requests
ab -n 100 -c 10 http://localhost:5000/api/signals
ab -n 100 -c 10 http://localhost:5000/api/portfolio
```

### Database Performance
```bash
# Test with large dataset
# Insert 10,000 signals
# Query time should be < 1 second
```

### Memory Usage
```bash
# Monitor memory during 24-hour run
# Expected: < 200MB
```

## Edge Case Testing

### Market Hours
- [ ] Agent pauses outside market hours (3:30 PM - 9:15 AM)
- [ ] Agent resumes at market open
- [ ] Weekend detection works correctly

### Data Validation
- [ ] Handles missing OHLCV data gracefully
- [ ] Handles invalid symbol tokens
- [ ] Handles network timeouts
- [ ] Handles API rate limits

### Error Handling
- [ ] Database connection errors logged
- [ ] Telegram send failures don't crash agent
- [ ] Angel One API errors handled gracefully
- [ ] Invalid configuration caught at startup

## Regression Testing

### After Each Update
1. Run all unit tests
2. Run integration tests
3. Manual smoke test (5 signals)
4. Verify database integrity
5. Check Telegram alerts
6. Verify dashboard loads

### Before Deployment
1. Full 24-hour test run
2. Backtest on 1-year data
3. Compare with baseline metrics
4. Verify all Telegram commands
5. Check dashboard responsiveness
6. Verify database backups

## Test Data

### Sample Signal
```python
{
    "symbol": "RELIANCE",
    "ltp": 2500.0,
    "action": "BUY",
    "score": 75,
    "confidence": "HIGH",
    "target": 2600.0,
    "sl": 2400.0,
    "reasons": [
        "RSI > 70 (Overbought)",
        "MACD bullish crossover",
        "Price above EMA20"
    ]
}
```

### Sample Position
```python
{
    "symbol": "RELIANCE",
    "quantity": 1,
    "entry_price": 2500.0,
    "entry_time": "2026-04-22 10:30:00",
    "exit_price": 2550.0,
    "exit_time": "2026-04-22 11:00:00",
    "pnl": 50.0,
    "status": "CLOSED"
}
```

## Continuous Testing

### Daily
- [ ] Agent running without crashes
- [ ] Signals generating on schedule
- [ ] Telegram alerts working
- [ ] Dashboard accessible

### Weekly
- [ ] Backtest results reviewed
- [ ] Win rate > 50%
- [ ] Drawdown < 15%
- [ ] No database errors

### Monthly
- [ ] Full regression test suite
- [ ] Performance benchmarks
- [ ] Security audit
- [ ] Dependency updates

## Test Automation

### GitHub Actions (CI/CD)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/
```

## Reporting

### Test Results Template
```
Date: 2026-04-22
Duration: 24 hours
Signals Generated: 48
Win Rate: 62.5%
Total P&L: +1250
Drawdown: 8.2%
Errors: 0
Status: PASS
```

## Support

For test failures:
1. Check logs in `logs/` directory
2. Verify .env configuration
3. Test components individually
4. Review error messages carefully
5. Check database integrity
