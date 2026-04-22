# Deployment Checklist - Angel One Trading Agent v1.0

## Pre-Deployment Verification

### Code Quality
- [ ] All Python files have no syntax errors
- [ ] No unused imports
- [ ] Consistent code formatting
- [ ] Docstrings on all classes and methods
- [ ] Error handling on all API calls
- [ ] Logging on critical operations

### Dependencies
- [ ] requirements.txt updated with all packages
- [ ] No conflicting versions
- [ ] All packages available on PyPI
- [ ] Tested on Python 3.8+
- [ ] No system-specific dependencies

### Configuration
- [ ] .env.example created with all variables
- [ ] .env file has valid credentials
- [ ] All required API keys obtained
- [ ] Risk parameters configured
- [ ] Telegram bot created and tested
- [ ] Finnhub API key obtained

### Database
- [ ] SQLite schema verified
- [ ] All 4 tables created correctly
- [ ] UNIQUE constraints in place
- [ ] Foreign keys configured
- [ ] Database file location set
- [ ] Backup strategy defined

### Security
- [ ] .gitignore includes .env
- [ ] No credentials in code
- [ ] No hardcoded API keys
- [ ] HTTPS enforced on Render
- [ ] Database access restricted
- [ ] Telegram token secured

---

## Local Testing (Before Deployment)

### Agent Testing
- [ ] Agent starts without errors
- [ ] Connects to Angel One API
- [ ] Generates first signal within 5 minutes
- [ ] Saves signal to database
- [ ] Saves signal to CSV
- [ ] Sends Telegram alert
- [ ] Logs to file correctly
- [ ] Handles market closed gracefully
- [ ] Resumes at market open

### Portfolio Testing
- [ ] BUY signal opens position
- [ ] Position saved to database
- [ ] SELL signal closes position
- [ ] P&L calculated correctly
- [ ] Portfolio summary accurate
- [ ] Win rate tracking works
- [ ] Metrics saved daily

### Risk Testing
- [ ] Position size calculated correctly
- [ ] Drawdown tracked accurately
- [ ] Trading pauses on threshold
- [ ] Risk alerts sent to Telegram
- [ ] Balance updates on P&L
- [ ] Peak balance recorded

### Dashboard Testing
- [ ] Dashboard loads at http://localhost:5000
- [ ] All 4 tabs functional
- [ ] Signals display correctly
- [ ] Portfolio shows open positions
- [ ] Risk metrics display
- [ ] Metrics chart loads
- [ ] Auto-refresh works
- [ ] Manual refresh works
- [ ] Responsive on mobile

### Backtester Testing
- [ ] Backtest runs without errors
- [ ] Metrics calculated correctly
- [ ] CSV report generated
- [ ] Results match manual calculation
- [ ] Date filtering works
- [ ] Capital calculation accurate

### Telegram Testing
- [ ] `/status` returns market status
- [ ] `/help` shows all commands
- [ ] `/portfolio` shows positions
- [ ] `/position SYMBOL` works
- [ ] Signal alerts received
- [ ] Error alerts received
- [ ] Startup message received

### 24-Hour Test Run
- [ ] Agent runs continuously
- [ ] No crashes or errors
- [ ] Signals generated on schedule
- [ ] Database grows correctly
- [ ] Dashboard updates in real-time
- [ ] Telegram alerts consistent
- [ ] Logs rotate properly
- [ ] Memory usage stable

---

## Render Deployment

### Repository Setup
- [ ] Code pushed to GitHub
- [ ] Repository is public
- [ ] .gitignore prevents .env commit
- [ ] README.md present
- [ ] Procfile present
- [ ] build.sh present
- [ ] requirements.txt present

### Render Web Service (Dashboard)
- [ ] Service created
- [ ] GitHub connected
- [ ] Build command: `bash build.sh`
- [ ] Start command: `cd dashboard && python app.py`
- [ ] Environment variables set:
  - [ ] TELEGRAM_BOT_TOKEN
  - [ ] TELEGRAM_CHAT_ID
  - [ ] FINNHUB_API_KEY
  - [ ] ACCOUNT_SIZE
  - [ ] RISK_PER_TRADE
  - [ ] MAX_DRAWDOWN_THRESHOLD
  - [ ] PORT=5000
- [ ] Service deployed successfully
- [ ] Dashboard accessible at https://your-app.onrender.com

### Render Worker Service (Agent)
- [ ] Service created
- [ ] GitHub connected
- [ ] Build command: `bash build.sh`
- [ ] Start command: `cd angel_agent && python agent.py`
- [ ] Environment variables set (same as web service)
- [ ] Service deployed successfully
- [ ] Logs show agent running

### Keep-Alive Setup
- [ ] UptimeRobot account created
- [ ] Monitor created for dashboard
- [ ] URL: https://your-app.onrender.com/api/health
- [ ] Interval: 5 minutes
- [ ] Monitor active

### Database Persistence
- [ ] data/ directory created
- [ ] trading_agent.db file exists
- [ ] Database persists across deployments
- [ ] Backup strategy documented

---

## Post-Deployment Verification

### Dashboard Access
- [ ] Dashboard loads: https://your-app.onrender.com
- [ ] All tabs functional
- [ ] API endpoints responding
- [ ] Real-time updates working
- [ ] No console errors

### Agent Status
- [ ] Agent running (check Render logs)
- [ ] Signals generating (check /api/signals)
- [ ] Database growing (check /api/metrics)
- [ ] Telegram alerts received
- [ ] No errors in logs

### Data Integrity
- [ ] Signals saved to database
- [ ] Positions tracked correctly
- [ ] P&L calculated accurately
- [ ] Metrics recorded daily
- [ ] CSV export working

### Telegram Integration
- [ ] Startup message received
- [ ] Signal alerts received
- [ ] Commands responding
- [ ] Error alerts working

### Performance
- [ ] Dashboard loads < 2 seconds
- [ ] API responses < 500ms
- [ ] Agent CPU usage < 10%
- [ ] Memory usage < 200MB
- [ ] Database queries < 1 second

---

## Monitoring & Maintenance

### Daily Checks
- [ ] Dashboard accessible
- [ ] Agent running (check logs)
- [ ] Signals generating
- [ ] Telegram alerts working
- [ ] No database errors

### Weekly Checks
- [ ] Win rate > 50%
- [ ] Drawdown < 15%
- [ ] No crashes in logs
- [ ] Database size reasonable
- [ ] Backtest results reviewed

### Monthly Checks
- [ ] Full regression test
- [ ] Performance benchmarks
- [ ] Security audit
- [ ] Dependency updates
- [ ] Database optimization

### Quarterly Checks
- [ ] Strategy review
- [ ] Parameter optimization
- [ ] Risk assessment
- [ ] Capacity planning
- [ ] Disaster recovery test

---

## Troubleshooting Guide

### Agent Not Starting
```bash
# Check logs
# Verify .env variables
# Test Angel One connection
# Check database permissions
```

### Dashboard Not Loading
```bash
# Check Flask is running
# Verify port 5000 available
# Check API endpoints
# Review browser console
```

### No Signals Generated
```bash
# Check market hours (9:15 AM - 3:30 PM IST)
# Verify symbol token
# Check Angel One API status
# Review agent logs
```

### Database Errors
```bash
# Check data/ directory exists
# Verify database file permissions
# Check disk space
# Reinitialize if corrupted
```

### Telegram Not Working
```bash
# Verify bot token
# Verify chat ID
# Test locally first
# Check Telegram API status
```

---

## Rollback Plan

### If Deployment Fails
1. Check Render logs for errors
2. Verify all environment variables
3. Test locally first
4. Fix issue in code
5. Push to GitHub
6. Redeploy on Render

### If Agent Crashes
1. Check logs for error
2. Verify database integrity
3. Restart worker service
4. Monitor for recurrence
5. Fix root cause

### If Dashboard Breaks
1. Check API endpoints
2. Verify database connection
3. Restart web service
4. Check browser console
5. Review Flask logs

### Database Corruption
1. Stop agent
2. Backup database
3. Reinitialize database
4. Restore from backup if needed
5. Restart agent

---

## Success Criteria

### Minimum Requirements
- [ ] Agent generates signals every 5 minutes
- [ ] Dashboard displays real-time data
- [ ] Telegram alerts working
- [ ] Database persisting data
- [ ] No crashes for 24 hours

### Recommended Requirements
- [ ] Win rate > 50%
- [ ] Drawdown < 15%
- [ ] Portfolio tracking accurate
- [ ] Risk management active
- [ ] Backtester functional

### Production Ready
- [ ] All minimum requirements met
- [ ] All recommended requirements met
- [ ] 7-day continuous run successful
- [ ] Backtest results validated
- [ ] Documentation complete

---

## Sign-Off

### Development Team
- [ ] Code review completed
- [ ] All tests passed
- [ ] Documentation reviewed
- [ ] Security audit passed

### QA Team
- [ ] Functional testing completed
- [ ] Performance testing passed
- [ ] Security testing passed
- [ ] User acceptance testing passed

### Operations Team
- [ ] Deployment procedure verified
- [ ] Monitoring configured
- [ ] Backup strategy tested
- [ ] Runbooks prepared

### Management
- [ ] Risk assessment approved
- [ ] Budget approved
- [ ] Timeline approved
- [ ] Go-live approved

---

## Deployment Date & Time

**Planned Deployment**: _______________
**Actual Deployment**: _______________
**Deployed By**: _______________
**Verified By**: _______________

---

## Post-Deployment Notes

```
[Space for deployment notes and observations]
```

---

## Contact Information

**Development Lead**: _______________
**Operations Lead**: _______________
**Support Contact**: _______________
**Emergency Contact**: _______________

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-22 | Team | Initial checklist |
| | | | |
| | | | |

---

**Last Updated**: 2026-04-22
**Status**: Ready for Deployment ✅
