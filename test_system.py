#!/usr/bin/env python3
"""
시스템 테스트 스크립트
Test the entire Investment Signal System
"""

import sys
import time
import json
from datetime import datetime
from loguru import logger

# 로깅 설정
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>"
)

def print_section(title):
    """섹션 제목 출력"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_imports():
    """필수 라이브러리 임포트 테스트"""
    print_section("1️⃣  필수 라이브러리 테스트")

    libraries = {
        "loguru": "로깅",
        "supabase": "데이터베이스",
        "anthropic": "Claude API",
        "flask": "웹 서버"
    }

    all_ok = True
    for lib, desc in libraries.items():
        try:
            __import__(lib)
            logger.info(f"✅ {lib:15} - {desc}")
        except ImportError:
            logger.error(f"❌ {lib:15} - {desc} (설치 필요: pip install {lib})")
            all_ok = False

    return all_ok

def test_environment():
    """환경 변수 테스트"""
    print_section("2️⃣  환경 변수 테스트")

    import os

    required_vars = {
        "ANTHROPIC_API_KEY": "Claude API 키",
        "SUPABASE_URL": "Supabase URL",
        "SUPABASE_KEY": "Supabase API 키"
    }

    optional_vars = {
        "ALERT_RECIPIENTS": "알림 수신자 이메일",
        "FINNHUB_API_KEY": "Finnhub API 키"
    }

    all_ok = True

    # 필수 변수
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            logger.info(f"✅ {var:20} = {masked}")
        else:
            logger.error(f"❌ {var:20} - 필수 (설정해주세요)")
            all_ok = False

    # 선택 변수
    print()
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            logger.info(f"⚠️  {var:20} = {masked} (선택)")
        else:
            logger.warning(f"⚠️  {var:20} - 미설정 (선택사항)")

    return all_ok

def test_database():
    """데이터베이스 연결 테스트"""
    print_section("3️⃣  데이터베이스 연결 테스트")

    try:
        from database.supabase_client import SupabaseClient

        db = SupabaseClient()
        logger.info("✅ Supabase 클라이언트 초기화 성공")

        # 간단한 조회 테스트
        try:
            # 테이블 존재 여부 확인 (read-only 쿼리)
            result = db.client.table("news_raw").select("count()", method="count").limit(1).execute()
            count = result.count if hasattr(result, 'count') else 0
            logger.info(f"✅ 뉴스 테이블: {count} items")

            result = db.client.table("analyzed_news").select("count()", method="count").limit(1).execute()
            count = result.count if hasattr(result, 'count') else 0
            logger.info(f"✅ 분석 테이블: {count} items")

            return True

        except Exception as e:
            logger.error(f"❌ 테이블 쿼리 실패: {str(e)[:100]}")
            return False

    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
        return False

def test_analyzer():
    """분석 시스템 테스트"""
    print_section("4️⃣  분석 시스템 테스트")

    try:
        from analyzers.relevance_analyzer import RelevanceAnalyzer

        analyzer = RelevanceAnalyzer()

        if analyzer.auto_analyze:
            logger.info("✅ Claude API 자동 분석 모드 활성화")
            logger.info("   - 병렬 분석 가능")
            logger.info("   - 배치 처리: 200개씩")
            logger.info("   - 신호 레벨 자동 분류")
            return True
        else:
            logger.warning("⚠️  수동 분석 모드 (Claude API 미설정)")
            logger.info("   - .env에 ANTHROPIC_API_KEY 설정 필요")
            return False

    except Exception as e:
        logger.error(f"❌ 분석 시스템 로드 실패: {e}")
        return False

def test_signal_api():
    """신호 API 테스트"""
    print_section("5️⃣  신호 API 테스트")

    try:
        from dashboard.signal_api import SignalAPI

        signal_api = SignalAPI()
        logger.info("✅ Signal API 초기화 성공")

        # 메서드 확인
        methods = [
            "get_signals_by_level",
            "get_urgent_signals",
            "get_trending_symbols",
            "get_dashboard_summary",
            "get_signals_for_article"
        ]

        for method in methods:
            if hasattr(signal_api, method):
                logger.info(f"✅ {method}()")
            else:
                logger.error(f"❌ {method}() - 메서드 없음")

        return True

    except Exception as e:
        logger.error(f"❌ Signal API 로드 실패: {e}")
        return False

def test_email_service():
    """이메일 알림 서비스 테스트"""
    print_section("6️⃣  이메일 알림 서비스 테스트")

    try:
        from alerts.email_alerts import EmailAlertService

        service = EmailAlertService()

        if service.sender_password:
            logger.info("✅ SMTP 인증 정보 설정됨")
            logger.info(f"   - 발신자: {service.sender_email}")
            logger.info(f"   - SMTP: {service.smtp_server}:{service.smtp_port}")
            return True
        else:
            logger.warning("⚠️  SMTP 비밀번호 미설정")
            logger.info("   - 이메일 알림 기능이 비활성화됨")
            logger.info("   - .env에 SENDER_PASSWORD 설정 필요")
            return False

    except Exception as e:
        logger.error(f"❌ 이메일 서비스 로드 실패: {e}")
        return False

def test_article_queue():
    """블로거 큐 시스템 테스트"""
    print_section("7️⃣  블로거 큐 시스템 테스트")

    try:
        from blogger.article_queue import ArticleQueueManager

        queue = ArticleQueueManager()
        logger.info("✅ Article Queue Manager 초기화 성공")

        # 메서드 확인
        methods = [
            "get_recommended_signals",
            "get_urgent_recommendations",
            "get_daily_article_suggestions",
            "get_smart_recommendations"
        ]

        for method in methods:
            if hasattr(queue, method):
                logger.info(f"✅ {method}()")
            else:
                logger.error(f"❌ {method}() - 메서드 없음")

        return True

    except Exception as e:
        logger.error(f"❌ Article Queue 로드 실패: {e}")
        return False

def test_scheduler():
    """작업 스케줄러 테스트"""
    print_section("8️⃣  작업 스케줄러 테스트")

    try:
        from scheduler.jobs import JobScheduler

        scheduler = JobScheduler()
        logger.info("✅ Job Scheduler 초기화 성공")

        # 작업 확인
        jobs = [
            "collect_news_job",
            "analyze_news_job",
            "generate_articles_job",
            "send_urgent_alerts_job",
            "send_daily_digest_job",
            "send_blog_recommendations_job"
        ]

        for job in jobs:
            if hasattr(scheduler, job):
                logger.info(f"✅ {job}()")
            else:
                logger.error(f"❌ {job}() - 작업 없음")

        return True

    except Exception as e:
        logger.error(f"❌ Scheduler 로드 실패: {e}")
        return False

def test_dashboard_server():
    """대시보드 서버 테스트"""
    print_section("9️⃣  대시보드 서버 테스트")

    try:
        from dashboard.server import create_app

        app = create_app()

        if app is None:
            logger.error("❌ Flask 미설치 또는 오류")
            return False

        logger.info("✅ Flask 앱 생성 성공")

        # 라우트 확인
        routes = [
            "/",
            "/api/health",
            "/api/signals/urgent",
            "/api/trending-symbols",
            "/api/dashboard"
        ]

        with app.test_client() as client:
            for route in routes:
                try:
                    response = client.get(route)
                    status = "✅" if response.status_code < 400 else "⚠️"
                    logger.info(f"{status} {route:30} ({response.status_code})")
                except Exception as e:
                    logger.error(f"❌ {route:30} - {str(e)[:50]}")

        return True

    except Exception as e:
        logger.error(f"❌ Dashboard Server 테스트 실패: {e}")
        return False

def test_data_pipeline():
    """데이터 처리 파이프라인 테스트"""
    print_section("🔟 데이터 처리 파이프라인 테스트")

    try:
        from database.models import AnalyzedNews, PriceImpact, Importance

        # 테스트 신호 생성
        test_signal = AnalyzedNews(
            raw_news_id="test-uuid",
            relevance_score=92,
            affected_symbols=["MSFT", "AAPL"],
            price_impact=PriceImpact.UP,
            importance=Importance.HIGH,
            signal_level=1,  # 자동으로 설정됨
            analysis={
                "reasoning": "Test signal",
                "key_points": ["Test point 1", "Test point 2"]
            }
        )

        # to_dict() 변환 테스트
        data = test_signal.to_dict()

        required_fields = [
            "raw_news_id", "relevance_score", "affected_symbols",
            "price_impact", "importance", "signal_level", "analysis"
        ]

        for field in required_fields:
            if field in data:
                logger.info(f"✅ {field:20} = {str(data[field])[:40]}")
            else:
                logger.error(f"❌ {field:20} - 필드 없음")

        return True

    except Exception as e:
        logger.error(f"❌ 데이터 모델 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     투자 시그널 대시보드 - 시스템 테스트                     ║
║  Investment Signal Dashboard - System Test                   ║
╚══════════════════════════════════════════════════════════════╝
""")

    results = {}

    # 모든 테스트 실행
    results["라이브러리"] = test_imports()
    results["환경 변수"] = test_environment()
    results["데이터베이스"] = test_database()
    results["분석 시스템"] = test_analyzer()
    results["신호 API"] = test_signal_api()
    results["이메일 서비스"] = test_email_service()
    results["블로거 큐"] = test_article_queue()
    results["스케줄러"] = test_scheduler()
    results["대시보드 서버"] = test_dashboard_server()
    results["데이터 파이프라인"] = test_data_pipeline()

    # 결과 요약
    print_section("📊 테스트 결과 요약")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status:8} | {test_name}")

    print(f"\n{'='*60}")
    print(f"  총 {total}개 테스트 중 {passed}개 통과 ({passed*100//total}%)")
    print(f"{'='*60}\n")

    if passed == total:
        logger.info("🎉 모든 테스트 통과! 시스템 준비 완료\n")
        logger.info("다음 단계:")
        logger.info("  1. python main.py --mode once     # 전체 실행 테스트")
        logger.info("  2. python dashboard/server.py      # 대시보드 시작")
        logger.info("  3. http://localhost:5000           # 브라우저에서 접속\n")
        return 0
    else:
        logger.warning(f"⚠️  {total - passed}개 테스트 실패\n")
        logger.info("문제 해결:")
        logger.info("  1. .env 파일 확인 (API 키 설정)")
        logger.info("  2. 필수 라이브러리 설치 (pip install -r requirements.txt)")
        logger.info("  3. Supabase 테이블 생성 (SYSTEM_IMPLEMENTATION.md 참고)\n")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
