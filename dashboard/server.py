"""
투자 시그널 대시보드 서버
Investment Signal Dashboard Server (Flask)
"""

import sys
import os
from datetime import datetime
from loguru import logger

sys.path.append('..')

try:
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask not installed - dashboard server unavailable")

from dashboard.signal_api import SignalAPI


def create_app():
    """Flask 앱 생성"""
    if not FLASK_AVAILABLE:
        logger.error("Flask is required for dashboard server")
        return None

    # 정적 파일 경로 설정
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    app = Flask(__name__, static_folder=static_path, static_url_path='/static')
    CORS(app)  # CORS 활성화

    signal_api = SignalAPI()

    # ==================== 홈 라우트 ====================

    @app.route('/', methods=['GET'])
    def index():
        """대시보드 메인 페이지"""
        return send_from_directory(static_path, 'index.html')

    # ==================== API 라우트 ====================

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """헬스 체크"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Investment Signal Dashboard"
        })

    @app.route('/api/signals/urgent', methods=['GET'])
    def get_urgent_signals():
        """긴급 시그널 (Level 1)"""
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 20, type=int)

        signals = signal_api.get_urgent_signals(hours=hours, limit=limit)
        return jsonify({
            "level": 1,
            "count": len(signals),
            "signals": signals
        })

    @app.route('/api/signals/high-priority', methods=['GET'])
    def get_high_priority_signals():
        """높은 우선순위 시그널 (Level 1-2)"""
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 30, type=int)

        signals = signal_api.get_high_priority_signals(hours=hours, limit=limit)
        return jsonify({
            "levels": [1, 2],
            "count": len(signals),
            "signals": signals
        })

    @app.route('/api/signals/by-level/<int:level>', methods=['GET'])
    def get_signals_by_level(level):
        """레벨별 시그널"""
        if level not in [1, 2, 3, 4]:
            return jsonify({"error": "Invalid level. Must be 1-4"}), 400

        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 50, type=int)

        signals = signal_api.get_signals_by_level(level, hours=hours, limit=limit)
        return jsonify({
            "level": level,
            "count": len(signals),
            "signals": signals
        })

    @app.route('/api/signals/by-symbol/<symbol>', methods=['GET'])
    def get_signals_by_symbol(symbol):
        """종목별 시그널"""
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 20, type=int)

        signals = signal_api.get_signals_by_symbol(symbol, hours=hours, limit=limit)
        return jsonify({
            "symbol": symbol,
            "count": len(signals),
            "signals": signals
        })

    @app.route('/api/trending-symbols', methods=['GET'])
    def get_trending_symbols():
        """트렌딩 종목"""
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 15, type=int)

        symbols = signal_api.get_trending_symbols(hours=hours, limit=limit)
        return jsonify({
            "count": len(symbols),
            "symbols": symbols
        })

    @app.route('/api/important-symbols', methods=['GET'])
    def get_important_symbols():
        """오늘 주목할 종목"""
        symbols = signal_api.get_important_symbols_today()
        return jsonify({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "count": len(symbols),
            "symbols": symbols
        })

    @app.route('/api/dashboard', methods=['GET'])
    def get_dashboard_summary():
        """대시보드 요약"""
        hours = request.args.get('hours', 24, type=int)

        summary = signal_api.get_dashboard_summary(hours=hours)
        return jsonify(summary)

    @app.route('/api/price-impact', methods=['GET'])
    def get_price_impact_summary():
        """가격 영향 요약"""
        hours = request.args.get('hours', 24, type=int)

        summary = signal_api.get_price_impact_summary(hours=hours)
        return jsonify({
            "period_hours": hours,
            "impact": summary
        })

    @app.route('/api/signals-for-article', methods=['GET'])
    def get_signals_for_article():
        """글 작성용 시그널"""
        tier = request.args.get('tier', 'tier_1', type=str)
        hours = request.args.get('hours', 24, type=int)

        signals = signal_api.get_signals_for_article(tier=tier, hours=hours)
        return jsonify({
            "tier": tier,
            "count": len(signals),
            "signals": signals
        })

    @app.route('/api/signal/<signal_id>/process', methods=['POST'])
    def mark_signal_processed(signal_id):
        """시그널 처리 표시"""
        success = signal_api.mark_signal_as_processed(signal_id)
        return jsonify({
            "signal_id": signal_id,
            "processed": success
        })

    # ==================== 에러 핸들링 ====================

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({"error": "Internal Server Error"}), 500

    return app


if __name__ == '__main__':
    if not FLASK_AVAILABLE:
        logger.error("Flask is required. Install it with: pip install flask flask-cors")
        sys.exit(1)

    app = create_app()
    logger.info("Starting Investment Signal Dashboard Server...")
    logger.info("API docs available at: http://localhost:5000/api/*")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
