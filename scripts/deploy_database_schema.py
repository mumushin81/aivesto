#!/usr/bin/env python3
"""
Supabase 데이터베이스 스키마 자동 배포 스크립트
news_tables_schema.sql을 Supabase에 배포합니다.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
import psycopg2

load_dotenv()


def get_postgres_connection():
    """Supabase PostgreSQL 연결"""
    # Supabase URL에서 프로젝트 ID 추출
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        logger.error("SUPABASE_URL이 .env에 설정되지 않았습니다")
        return None

    # URL에서 프로젝트 ID 추출: https://xxx.supabase.co -> xxx
    project_id = supabase_url.replace("https://", "").replace(".supabase.co", "")

    # PostgreSQL 연결 정보
    host = f"db.{project_id}.supabase.co"
    database = "postgres"
    user = "postgres"

    # 비밀번호 환경 변수에서 가져오기
    password = os.getenv("SUPABASE_DB_PASSWORD")
    if not password:
        logger.error("❌ SUPABASE_DB_PASSWORD가 .env에 설정되지 않았습니다")
        logger.info("Supabase Dashboard > Settings > Database > Database password 에서 확인하세요")
        return None

    logger.info(f"Supabase 프로젝트: {project_id}")
    logger.info(f"Host: {host}")
    logger.info("")

    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=5432
        )
        logger.success("✅ PostgreSQL 연결 성공")
        return conn
    except Exception as e:
        logger.error(f"❌ PostgreSQL 연결 실패: {e}")
        logger.info("비밀번호를 확인하거나 Supabase 대시보드 Settings > Database에서 확인하세요")
        return None


def deploy_schema(conn, schema_path):
    """스키마 SQL 파일 실행"""
    try:
        # SQL 파일 읽기
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        # 커서 생성
        cursor = conn.cursor()

        logger.info("📊 스키마 배포 시작...")
        logger.info("=" * 60)

        # SQL 실행
        cursor.execute(sql)
        conn.commit()

        logger.success("✅ 스키마 배포 완료!")
        logger.info("=" * 60)

        # 테이블 확인
        logger.info("📋 생성된 테이블 확인 중...")
        cursor.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename LIKE '%news%'
            ORDER BY tablename
        """)

        tables = cursor.fetchall()
        if tables:
            logger.success(f"✅ {len(tables)}개 테이블 생성 확인:")
            for table in tables:
                logger.info(f"  - {table[0]}")
        else:
            logger.warning("⚠️  'news' 관련 테이블이 발견되지 않았습니다")

        # 뷰 확인
        logger.info("")
        logger.info("📋 생성된 뷰 확인 중...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            AND table_name = 'all_trading_signals'
        """)

        views = cursor.fetchall()
        if views:
            logger.success(f"✅ {len(views)}개 뷰 생성 확인:")
            for view in views:
                logger.info(f"  - {view[0]}")
        else:
            logger.warning("⚠️  'all_trading_signals' 뷰가 발견되지 않았습니다")

        # RLS 정책 확인
        logger.info("")
        logger.info("🔒 RLS 정책 확인 중...")
        cursor.execute("""
            SELECT tablename, COUNT(*) as policy_count
            FROM pg_policies
            WHERE schemaname = 'public'
            AND tablename LIKE '%news%'
            GROUP BY tablename
            ORDER BY tablename
        """)

        policies = cursor.fetchall()
        if policies:
            logger.success(f"✅ RLS 정책 설정 확인:")
            for table, count in policies:
                logger.info(f"  - {table}: {count}개 정책")
        else:
            logger.warning("⚠️  RLS 정책이 발견되지 않았습니다")

        cursor.close()
        return True

    except Exception as e:
        logger.error(f"❌ 스키마 배포 실패: {e}")
        conn.rollback()
        return False


def test_insert(conn):
    """테스트 데이터 삽입 및 조회"""
    try:
        cursor = conn.cursor()

        logger.info("")
        logger.info("=" * 60)
        logger.info("🧪 테스트 데이터 삽입 중...")
        logger.info("=" * 60)

        # 테스트 데이터 삽입
        test_sql = """
        INSERT INTO tech_trends (
            trend_type,
            title,
            source,
            companies,
            signal,
            impact_score
        ) VALUES (
            'AI_CHIP',
            'Test: NVIDIA announces new AI chip',
            'Test Script',
            '["NVDA", "MSFT"]'::jsonb,
            'TEST_SIGNAL',
            95
        ) RETURNING id;
        """

        cursor.execute(test_sql)
        test_id = cursor.fetchone()[0]
        conn.commit()

        logger.success(f"✅ 테스트 데이터 삽입 성공 (ID: {test_id})")

        # 데이터 조회
        cursor.execute(f"SELECT * FROM tech_trends WHERE id = '{test_id}'")
        result = cursor.fetchone()

        if result:
            logger.success("✅ 테스트 데이터 조회 성공")
            logger.info(f"  - 제목: {result[2]}")
            logger.info(f"  - 시그널: {result[5]}")
            logger.info(f"  - Impact Score: {result[6]}")

        # 통합 뷰 확인
        cursor.execute("""
            SELECT signal_category, signal, impact_level
            FROM all_trading_signals
            WHERE signal = 'TEST_SIGNAL'
        """)
        view_result = cursor.fetchone()

        if view_result:
            logger.success("✅ 통합 뷰(all_trading_signals) 정상 작동")
            logger.info(f"  - 카테고리: {view_result[0]}")
            logger.info(f"  - 시그널: {view_result[1]}")
            logger.info(f"  - Impact: {view_result[2]}")

        # 테스트 데이터 삭제
        cursor.execute(f"DELETE FROM tech_trends WHERE id = '{test_id}'")
        conn.commit()
        logger.info("🧹 테스트 데이터 삭제 완료")

        cursor.close()
        return True

    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}")
        conn.rollback()
        return False


def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("🚀 Supabase 데이터베이스 스키마 배포")
    logger.info("=" * 60)
    logger.info("")

    # 스키마 파일 경로
    schema_path = Path(__file__).parent.parent / "database" / "news_tables_schema.sql"

    if not schema_path.exists():
        logger.error(f"❌ 스키마 파일을 찾을 수 없습니다: {schema_path}")
        return 1

    logger.info(f"📄 스키마 파일: {schema_path}")
    logger.info("")

    # PostgreSQL 연결
    conn = get_postgres_connection()
    if not conn:
        return 1

    # 스키마 배포
    if not deploy_schema(conn, schema_path):
        conn.close()
        return 1

    # 테스트 실행
    if not test_insert(conn):
        conn.close()
        return 1

    conn.close()

    logger.info("")
    logger.info("=" * 60)
    logger.success("🎉 데이터베이스 배포 완료!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("다음 단계:")
    logger.info("  1. 뉴스 수집기 실행: python scripts/news_collectors/tech_trends_collector.py")
    logger.info("  2. 블로그 생성: python scripts/generate_blog_from_signals.py")
    logger.info("")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
