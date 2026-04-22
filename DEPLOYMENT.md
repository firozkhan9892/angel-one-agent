# Deployment Guide - Angel One Trading Agent

## Local Development

### 1. Setup Environment
```bash
# Clone and navigate
git clone <repo-url>
cd angel_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials
```bash
# Copy and edit .env
cp .env.example .env

# Add your credentials:
# - Angel One API credentials
# - Telegram bot token and chat ID
# - Finnhub API key
# - Risk management parameters
```

### 3. Run Locally
```bash
# Terminal 1: Run agent
python agent.py --symbol RELIANCE --interval FIVE_MINUTE

# Terminal 2: Run dashboard
cd dashboard
python app.py
# Access at http://localhost:5000
```

## Deployment on Render (Free Tier)

### Step 1: Prepare Repository
```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit: Angel One Trading Agent with advanced features"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/angel-one-agent.git
git push -u origin main
```

### Step 2: Create Render Services

#### Service 1: Web Dashboard
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: `angel-trading-dashboard`
   - **Environment**: Python 3
   - **Build Command**: `bash build.sh`
   - **Start Command**: `cd dashboard && python app.py`
   - **Plan**: Free
5. Add Environment Variables (from .env):
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `FINNHUB_API_KEY`
   - `ACCOUNT_SIZE`
   - `RISK_PER_TRADE`
   - `MAX_DRAWDOWN_THRESHOLD`
   - `PORT=5000`
6. Deploy

#### Service 2: Background Worker (Agent)
1. Click "New +" → "Background Worker"
2. Connect same GitHub repository
3. Configure:
   - **Name**: `angel-trading-agent`
   - **Environment**: Python 3
   - **Build Command**: `bash build.sh`
   - **Start Command**: `cd angel_agent && python agent.py`
   - **Plan**: Free
4. Add same Environment Variables
5. Deploy

### Step 3: Setup Keep-Alive (Prevent Spin-Down)

Free Render services spin down after 15 minutes of inactivity. Use UptimeRobot:

1. Go to https://uptimerobot.com
2. Sign up (free account)
3. Create new monitor:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: `Angel Trading Dashboard`
   - **URL**: `https://your-app.onrender.com/api/health`
   - **Monitoring Interval**: 5 minutes
4. Save

This pings your dashboard every 5 minutes, keeping it alive.

### Step 4: Verify Deployment

```bash
# Check dashboard
curl https://your-app.onrender.com/api/health

# Check logs
# In Render dashboard → Service → Logs
```

## Database Persistence

SQLite database is stored at `data/trading_agent.db`. On Render free tier:
- Database persists across deployments
- Data is lost if service is deleted
- For production, migrate to PostgreSQL

### Backup Database
```bash
# Download from Render
# In Render dashboard → Service → Shell
# Run: sqlite3 data/trading_agent.db ".dump" > backup.sql
```

## Monitoring & Maintenance

### Daily Checks
1. Dashboard loads: `https://your-app.onrender.com`
2. Agent is running: Check Render logs
3. Signals are generating: Check `/api/signals`
4. Portfolio is tracking: Check `/api/portfolio`

### Weekly Tasks
1. Review backtest results
2. Check drawdown metrics
3. Verify Telegram alerts working
4. Monitor win rate trends

### Monthly Tasks
1. Optimize indicator parameters
2. Review risk settings
3. Backup database
4. Update dependencies

## Troubleshooting

### Agent Not Starting
```bash
# Check logs in Render dashboard
# Common issues:
# 1. Missing .env variables
# 2. Angel One API credentials invalid
# 3. Database initialization failed

# Test locally first:
python agent.py --symbol RELIANCE
```

### Dashboard Not Loading
```bash
# Check Flask is running
curl https://your-app.onrender.com/

# Check API endpoints
curl https://your-app.onrender.com/api/health

# Review Render logs for errors
```

### Database Errors
```bash
# Check database exists
# In Render shell: ls -la data/

# Verify database integrity
# In Render shell: sqlite3 data/trading_agent.db ".tables"

# Reinitialize if corrupted
# In Render shell: rm data/trading_agent.db
# Restart service
```

### Telegram Not Working
```bash
# Verify credentials in .env
# Test locally:
python -c "from modules.telegram_notifier import TelegramNotifier; TelegramNotifier().send_error('Test')"

# Check Telegram bot token is valid
# Check chat ID is correct
```

## Performance Optimization

### For Free Tier
- Use FIVE_MINUTE interval (not ONE_MINUTE)
- Limit to 1-2 symbols
- Keep dashboard refresh at 5 seconds
- Archive old signals monthly

### Database Optimization
```sql
-- In Render shell
sqlite3 data/trading_agent.db "VACUUM;"
sqlite3 data/trading_agent.db "ANALYZE;"
```

### Memory Management
- Agent uses ~50MB RAM
- Dashboard uses ~100MB RAM
- Total: ~150MB (well within free tier limit)

## Scaling to Production

### Upgrade to Paid Tier
1. In Render dashboard → Service → Settings
2. Change Plan from Free to Starter ($7/month)
3. Benefits:
   - No spin-down
   - 0.5 CPU, 512MB RAM
   - Persistent storage
   - Custom domain

### Migrate to PostgreSQL
```bash
# Create PostgreSQL database on Render
# Update database.py to use PostgreSQL
# Migrate data from SQLite
```

### Add SSL Certificate
- Render provides free SSL automatically
- Access via `https://your-app.onrender.com`

## Security Best Practices

### Credentials
- Never commit `.env` to git
- Use Render environment variables
- Rotate API keys monthly
- Use separate credentials for testing

### Database
- Enable database backups
- Encrypt sensitive data
- Limit database access
- Monitor for unauthorized access

### API
- Use HTTPS only
- Implement rate limiting
- Add authentication for dashboard
- Log all API calls

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Angel One API**: https://smartapi.angelbroking.com/
- **Finnhub API**: https://finnhub.io/docs/api
- **Telegram Bot API**: https://core.telegram.org/bots/api

## Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] .env configured with all credentials
- [ ] Render web service created and deployed
- [ ] Render worker service created and deployed
- [ ] UptimeRobot monitor configured
- [ ] Dashboard accessible at https://your-app.onrender.com
- [ ] Agent logs showing signals generated
- [ ] Telegram alerts working
- [ ] Database initialized with tables
- [ ] Backtest script tested locally
- [ ] Documentation reviewed

## Next Steps

1. Deploy to Render
2. Monitor for 24 hours
3. Verify all signals and alerts working
4. Run backtest on historical data
5. Adjust risk parameters based on results
6. Scale to multiple symbols if needed
