#!/usr/bin/env python3
"""
Supabase RPC를 통한 스키마 배포
REST API로 직접 SQL 실행
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
import requests

load_dotenv()


def execute_sql_via_api(sql_statements):
    """Supabase SQL API를 통해 DDL 실행"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않았습니다")
        return False

    # Supabase는 REST API로 DDL을 실행할 수 없으므로
    # 직접 테이블을 하나씩 생성하는 방법을 사용합니다

    logger.info("⚠️  Supabase REST API는 DDL(CREATE TABLE)을 직접 지원하지 않습니다")
    logger.info("대신 Python SDK를 사용하여 테이블 구조를 확인합니다")

    return False


def create_tables_manually():
    """Python으로 직접 테이블 생성 (Supabase Admin API 사용)"""
    from supabase import create_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    supabase = create_client(supabase_url, supabase_key)

    logger.info("📊 Supabase 연결 확인 중...")

    # 기존 테이블 확인
    try:
        # tech_trends 테이블이 있는지 확인
        result = supabase.table('tech_trends').select('*').limit(1).execute()
        logger.success("✅ tech_trends 테이블이 이미 존재합니다")
        return True
    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg or "PGRST205" in error_msg:
            logger.warning("⚠️  테이블이 아직 생성되지 않았습니다")
            logger.info("=" * 60)
            logger.info("📋 수동 배포 안내")
            logger.info("=" * 60)
            logger.info("")
            logger.info("Supabase는 REST API로 테이블 생성(DDL)을 지원하지 않습니다.")
            logger.info("다음 방법 중 하나를 선택하세요:")
            logger.info("")
            logger.info("방법 1: Supabase Dashboard (가장 쉬움)")
            logger.info("  1. https://supabase.com/dashboard 접속")
            logger.info("  2. SQL Editor 메뉴 클릭")
            logger.info("  3. 아래 명령어로 SQL 복사:")
            logger.info("     cat /Users/jinxin/dev/aivesto/database/news_tables_schema.sql | pbcopy")
            logger.info("  4. SQL Editor에 붙여넣기 후 Run 클릭")
            logger.info("")
            logger.info("방법 2: 데이터베이스 비밀번호 사용")
            logger.info("  1. Supabase Dashboard > Settings > Database에서 비밀번호 확인")
            logger.info("  2. .env 파일에 추가:")
            logger.info("     SUPABASE_DB_PASSWORD=여기에_비밀번호")
            logger.info("  3. 스크립트 실행:")
            logger.info("     python scripts/deploy_database_schema.py")
            logger.info("")
            return False
        else:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            return False


def check_schema_deployed():
    """스키마가 배포되었는지 확인"""
    from supabase import create_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    supabase = create_client(supabase_url, supabase_key)

    tables_to_check = [
        'tech_trends',
        'macro_news',
        'earnings_news',
        'sector_news',
        'corporate_events',
        'geopolitical_news'
    ]

    logger.info("=" * 60)
    logger.info("🔍 데이터베이스 스키마 확인 중...")
    logger.info("=" * 60)
    logger.info("")

    existing_tables = []
    missing_tables = []

    for table in tables_to_check:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            logger.success(f"✅ {table} - 존재함")
            existing_tables.append(table)
        except Exception as e:
            error_msg = str(e)
            if "Could not find the table" in error_msg or "PGRST205" in error_msg:
                logger.error(f"❌ {table} - 없음")
                missing_tables.append(table)
            else:
                logger.warning(f"⚠️  {table} - 확인 실패: {e}")

    logger.info("")
    logger.info("=" * 60)
    logger.info(f"📊 결과: {len(existing_tables)}/{len(tables_to_check)} 테이블 존재")
    logger.info("=" * 60)

    if len(existing_tables) == len(tables_to_check):
        logger.success("🎉 모든 테이블이 정상적으로 배포되었습니다!")
        return True
    else:
        logger.warning(f"⚠️  {len(missing_tables)}개 테이블이 없습니다")
        logger.info("Supabase Dashboard에서 스키마를 배포해주세요")
        return False


def print_deployment_guide():
    """배포 가이드 출력"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("📖 빠른 배포 가이드")
    logger.info("=" * 60)
    logger.info("")

    schema_path = "/Users/jinxin/dev/aivesto/database/news_tables_schema.sql"

    logger.info("1️⃣  터미널에서 SQL 복사:")
    logger.info(f"   cat {schema_path} | pbcopy")
    logger.info("")

    logger.info("2️⃣  Supabase Dashboard 접속:")
    logger.info("   https://supabase.com/dashboard")
    logger.info("")

    logger.info("3️⃣  SQL Editor에서 실행:")
    logger.info("   - SQL Editor 메뉴 클릭")
    logger.info("   - New query 버튼")
    logger.info("   - 복사한 SQL 붙여넣기 (Cmd+V)")
    logger.info("   - Run 버튼 클릭")
    logger.info("")

    logger.info("4️⃣  배포 확인:")
    logger.info("   python scripts/deploy_schema_via_rpc.py")
    logger.info("")

    # SQL 복사 명령어 실행
    logger.info("💡 자동으로 SQL을 클립보드에 복사합니다...")
    import subprocess
    try:
        subprocess.run(['pbcopy'], input=open(schema_path).read().encode(), check=True)
        logger.success("✅ SQL이 클립보드에 복사되었습니다!")
        logger.info("   Supabase SQL Editor에서 Cmd+V로 붙여넣으세요")
    except Exception as e:
        logger.warning(f"⚠️  자동 복사 실패: {e}")
        logger.info(f"   수동으로 복사: cat {schema_path} | pbcopy")


def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("🚀 Supabase 데이터베이스 스키마 확인")
    logger.info("=" * 60)
    logger.info("")

    # 스키마 배포 확인
    if check_schema_deployed():
        logger.info("")
        logger.info("다음 단계:")
        logger.info("  python scripts/news_collectors/tech_trends_collector.py")
        return 0
    else:
        logger.info("")
        print_deployment_guide()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
