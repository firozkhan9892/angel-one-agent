"""
Dashboard Backend - Flask API
Real-time monitoring of signals, portfolio, and performance
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import sys
from logzero import logger

# Add angel_agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'angel_agent'))

from modules.database import Database
from modules.portfolio_manager import PortfolioManager
from modules.risk_manager import RiskManager

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

try:
    db = Database()
    portfolio = PortfolioManager(db)
    risk_mgr = RiskManager()
except Exception as e:
    logger.warning(f"Could not initialize services: {e}")
    db = None
    portfolio = None
    risk_mgr = None


@app.route('/')
def index():
    """Serve dashboard homepage."""
    return render_template('index.html')


@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get recent signals."""
    try:
        signals = db.get_signals(limit=20)
        return jsonify({
            "status": "success",
            "data": [dict(s) for s in signals],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Get signals error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get portfolio summary."""
    try:
        summary = portfolio.get_portfolio_summary()
        return jsonify({
            "status": "success",
            "data": summary,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Get portfolio error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get open positions."""
    try:
        positions = portfolio.get_open_positions()
        return jsonify({
            "status": "success",
            "data": [dict(p) for p in positions],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Get positions error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/risk', methods=['GET'])
def get_risk():
    """Get risk metrics."""
    try:
        dd_info = risk_mgr.get_current_drawdown()
        return jsonify({
            "status": "success",
            "data": {
                **dd_info,
                "should_trade": risk_mgr.should_trade(),
                "risk_per_trade": risk_mgr.risk_per_trade * 100
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Get risk error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get performance metrics."""
    try:
        metrics = db.get_metrics(days=30)
        return jsonify({
            "status": "success",
            "data": [dict(m) for m in metrics],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Get metrics error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Angel One Trading Dashboard"
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({"status": "error", "message": "Internal server error"}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    logger.info(f"Starting dashboard on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
