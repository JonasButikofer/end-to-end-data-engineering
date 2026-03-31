"""
Mock REST API for testing the web analytics Prefect flow.

Usage:
    python mock_api.py

Then test with:
    curl http://localhost:5001/analytics/clickstream

This returns 50 random clickstream events matching the expected API schema.
"""

from flask import Flask, jsonify
from datetime import datetime, timedelta
import random

app = Flask(__name__)


@app.route('/analytics/clickstream', methods=['GET'])
def get_clickstream():
    """Return mock web analytics data."""
    events = []
    for i in range(50):
        events.append({
            'customer_id': random.randint(1, 100),
            'product_id': random.randint(1, 50),
            'session_id': f"session_{random.randint(1000, 9999)}",
            'page_url': f"https://adventure-works.com/product/{random.randint(1, 50)}",
            'event_type': random.choice(['page_view', 'click', 'add_to_cart', 'purchase']),
            'timestamp': (datetime.utcnow() - timedelta(minutes=random.randint(0, 60))).isoformat() + 'Z'
        })
    return jsonify(events)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
