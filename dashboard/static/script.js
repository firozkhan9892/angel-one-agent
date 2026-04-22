// Dashboard JavaScript - Real-time updates and interactions

const API_BASE = '/api';
const REFRESH_INTERVAL = 5000; // 5 seconds

let refreshTimer = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupRefreshButton();
    updateClock();
    loadAllData();
    setInterval(updateClock, 1000);
    setInterval(loadAllData, REFRESH_INTERVAL);
});

// Tab switching
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');

            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        });
    });
}

// Refresh button
function setupRefreshButton() {
    const refreshBtn = document.getElementById('refresh-btn');
    refreshBtn.addEventListener('click', () => {
        refreshBtn.disabled = true;
        refreshBtn.textContent = 'Refreshing...';
        loadAllData().then(() => {
            refreshBtn.disabled = false;
            refreshBtn.textContent = 'Refresh Now';
        });
    });
}

// Update clock
function updateClock() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString();
    document.getElementById('last-update').textContent = now.toLocaleTimeString();
}

// Load all data
async function loadAllData() {
    try {
        await Promise.all([
            loadSignals(),
            loadPortfolio(),
            loadPositions(),
            loadRisk(),
            loadMetrics()
        ]);
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Load signals
async function loadSignals() {
    try {
        const response = await fetch(`${API_BASE}/signals`);
        const result = await response.json();

        if (result.status === 'success') {
            const signalsList = document.getElementById('signals-list');
            signalsList.innerHTML = '';

            if (result.data.length === 0) {
                signalsList.innerHTML = '<p class="loading">No signals yet</p>';
                return;
            }

            result.data.forEach(signal => {
                const item = createSignalItem(signal);
                signalsList.appendChild(item);
            });
        }
    } catch (error) {
        console.error('Error loading signals:', error);
    }
}

// Create signal item
function createSignalItem(signal) {
    const item = document.createElement('div');
    const action = signal.action || 'HOLD';
    item.className = `signal-item ${action.toLowerCase()}`;

    const timestamp = new Date(signal.timestamp).toLocaleString();

    item.innerHTML = `
        <div class="signal-header">
            <span class="signal-symbol">${signal.symbol}</span>
            <span class="signal-action ${action.toLowerCase()}">${action}</span>
        </div>
        <div class="signal-details">
            <div class="detail-item">
                <span class="detail-label">LTP</span>
                <span class="detail-value">₹${parseFloat(signal.ltp).toFixed(2)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Score</span>
                <span class="detail-value">${signal.score || 0}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Confidence</span>
                <span class="detail-value">${signal.confidence || 'N/A'}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Target</span>
                <span class="detail-value">₹${parseFloat(signal.target).toFixed(2)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">SL</span>
                <span class="detail-value">₹${parseFloat(signal.sl).toFixed(2)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Time</span>
                <span class="detail-value">${timestamp}</span>
            </div>
        </div>
    `;

    return item;
}

// Load portfolio
async function loadPortfolio() {
    try {
        const response = await fetch(`${API_BASE}/portfolio`);
        const result = await response.json();

        if (result.status === 'success') {
            const data = result.data;
            document.getElementById('open-positions').textContent = data.open_positions_count || 0;
            document.getElementById('open-pnl').textContent = `₹${parseFloat(data.open_pnl).toFixed(2)}`;
            document.getElementById('closed-pnl').textContent = `₹${parseFloat(data.closed_pnl).toFixed(2)}`;
            document.getElementById('total-pnl').textContent = `₹${parseFloat(data.total_pnl).toFixed(2)}`;
            document.getElementById('win-rate').textContent = `${parseFloat(data.win_rate).toFixed(1)}%`;
            document.getElementById('winning-signals').textContent = data.winning_signals || 0;
            document.getElementById('losing-signals').textContent = data.losing_signals || 0;
            document.getElementById('total-signals').textContent = data.total_signals || 0;
        }
    } catch (error) {
        console.error('Error loading portfolio:', error);
    }
}

// Load positions
async function loadPositions() {
    try {
        const response = await fetch(`${API_BASE}/positions`);
        const result = await response.json();

        if (result.status === 'success') {
            const positionsList = document.getElementById('positions-list');
            positionsList.innerHTML = '';

            if (result.data.length === 0) {
                positionsList.innerHTML = '<p class="loading">No open positions</p>';
                return;
            }

            result.data.forEach(position => {
                const item = createPositionItem(position);
                positionsList.appendChild(item);
            });
        }
    } catch (error) {
        console.error('Error loading positions:', error);
    }
}

// Create position item
function createPositionItem(position) {
    const item = document.createElement('div');
    item.className = 'position-item';

    const entryTime = new Date(position.entry_time).toLocaleString();

    item.innerHTML = `
        <div class="signal-header">
            <span class="signal-symbol">${position.symbol}</span>
            <span class="signal-action buy">${position.status}</span>
        </div>
        <div class="signal-details">
            <div class="detail-item">
                <span class="detail-label">Quantity</span>
                <span class="detail-value">${position.quantity}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Entry Price</span>
                <span class="detail-value">₹${parseFloat(position.entry_price).toFixed(2)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Entry Time</span>
                <span class="detail-value">${entryTime}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">P&L</span>
                <span class="detail-value">₹${parseFloat(position.pnl || 0).toFixed(2)}</span>
            </div>
        </div>
    `;

    return item;
}

// Load risk metrics
async function loadRisk() {
    try {
        const response = await fetch(`${API_BASE}/risk`);
        const result = await response.json();

        if (result.status === 'success') {
            const data = result.data;
            document.getElementById('account-size').textContent = `₹${parseFloat(data.current_balance).toFixed(2)}`;
            document.getElementById('current-balance').textContent = `₹${parseFloat(data.current_balance).toFixed(2)}`;
            document.getElementById('peak-balance').textContent = `₹${parseFloat(data.peak_balance).toFixed(2)}`;
            document.getElementById('current-drawdown').textContent = `${parseFloat(data.current_drawdown_pct).toFixed(2)}%`;
            document.getElementById('max-drawdown').textContent = `${parseFloat(data.max_drawdown_pct).toFixed(2)}%`;
            document.getElementById('drawdown-amount').textContent = `₹${parseFloat(data.drawdown_amount).toFixed(2)}`;
            document.getElementById('risk-per-trade').textContent = `${data.risk_per_trade.toFixed(1)}%`;

            const status = data.should_trade ? 'ACTIVE' : 'PAUSED';
            const statusEl = document.getElementById('trading-status');
            statusEl.textContent = status;
            statusEl.style.color = data.should_trade ? '#4caf50' : '#f44336';
        }
    } catch (error) {
        console.error('Error loading risk:', error);
    }
}

// Load metrics
async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`);
        const result = await response.json();

        if (result.status === 'success') {
            const metricsList = document.getElementById('metrics-list');
            metricsList.innerHTML = '';

            if (result.data.length === 0) {
                metricsList.innerHTML = '<p class="loading">No metrics available</p>';
                return;
            }

            result.data.forEach(metric => {
                const item = createMetricItem(metric);
                metricsList.appendChild(item);
            });
        }
    } catch (error) {
        console.error('Error loading metrics:', error);
    }
}

// Create metric item
function createMetricItem(metric) {
    const item = document.createElement('div');
    item.className = 'metric-item';

    item.innerHTML = `
        <div class="signal-header">
            <span class="signal-symbol">Date: ${metric.date}</span>
        </div>
        <div class="signal-details">
            <div class="detail-item">
                <span class="detail-label">Total Signals</span>
                <span class="detail-value">${metric.total_signals || 0}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Winning</span>
                <span class="detail-value">${metric.winning_signals || 0}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Losing</span>
                <span class="detail-value">${metric.losing_signals || 0}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Win Rate</span>
                <span class="detail-value">${parseFloat(metric.win_rate).toFixed(1)}%</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Total P&L</span>
                <span class="detail-value">₹${parseFloat(metric.total_pnl).toFixed(2)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Max Drawdown</span>
                <span class="detail-value">${parseFloat(metric.max_drawdown).toFixed(2)}%</span>
            </div>
        </div>
    `;

    return item;
}
