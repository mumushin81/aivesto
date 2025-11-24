#!/usr/bin/env python3
"""
Supabase 데이터베이스에 스키마를 생성하는 스크립트
PostgreSQL 직접 연결 사용
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def extract_project_ref(url):
    """Supabase URL에서 프로젝트 ref 추출"""
    # https://czubqsnahmtdsmnyawlk.supabase.co -> czubqsnahmtdsmnyawlk
    return url.replace("https://", "").replace(".supabase.co", "")

def create_schema_with_psycopg2():
    """psycopg2를 사용하여 스키마 생성"""
    try:
        import psycopg2
    except ImportError:
        print("❌ psycopg2가 설치되지 않았습니다. 설치 중...")
        os.system("pip3 install -q psycopg2-binary")
        import psycopg2

    project_ref = extract_project_ref(SUPABASE_URL)

    print(f"\n{'='*80}")
    print("🔧 Supabase 데이터베이스 스키마 생성")
    print(f"{'='*80}")
    print(f"프로젝트: {project_ref}")
    print(f"{'='*80}\n")

    # PostgreSQL 연결 정보
    # Supabase는 database password가 별도로 필요합니다
    print("⚠️  PostgreSQL 연결을 위해 데이터베이스 비밀번호가 필요합니다.")
    print("   Supabase Dashboard → Settings → Database → Database password")
    print()

    db_password = input("데이터베이스 비밀번호를 입력하세요 (또는 Enter로 건너뛰기): ").strip()

    if not db_password:
        print("\n❌ 비밀번호가 제공되지 않았습니다.")
        print("\n다른 방법으로 스키마를 생성하세요:")
        print("1. Supabase Dashboard → SQL Editor")
        print("2. database/schema.sql 파일의 내용을 복사하여 붙여넣기")
        print("3. Run 버튼 클릭")
        return False

    # 연결 문자열 구성
    conn_params = {
        "host": f"db.{project_ref}.supabase.co",
        "port": 5432,
        "database": "postgres",
        "user": "postgres",
        "password": db_password
    }

    try:
        print("\n🔌 데이터베이스 연결 중...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        print("✅ 연결 성공!")
        print("\n📝 스키마 파일 읽는 중...")

        # schema.sql 읽기
        with open("database/schema.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()

        print("🚀 스키마 실행 중...")
        cursor.execute(schema_sql)
        conn.commit()

        print("\n✅ 스키마 생성 완료!")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n대안: Supabase Dashboard에서 수동으로 실행하세요:")
        print("1. https://supabase.com/dashboard → SQL Editor")
        print("2. database/schema.sql 내용 복사 & 붙여넣기")
        print("3. Run 클릭")
        return False

def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)

    success = create_schema_with_psycopg2()

    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
